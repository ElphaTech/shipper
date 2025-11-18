import atexit
import os
import re
import signal
import subprocess
import threading
import time
from pathlib import Path

from functions.command_runner import run_terminal_command
from functions.compressor import encode_video
from functions.config import PROJECT_ROOT, load_config
from functions.file_handler import load_json, save_json
import functions.logger  # Needed for logging
import functions.job_creation as jc

# Set working directory to script directory
script_path = os.path.abspath(__file__)
script_directory = os.path.dirname(script_path)
os.chdir(script_directory)

# == Import configuration ==
CONFIG = load_config()
maxencodejobs = CONFIG.max_encode_jobs
maxframecountjobs = CONFIG.max_frame_count_jobs
qualitypresets = CONFIG.quality_presets

DATA_FILE_PATH = PROJECT_ROOT / "data.json"

# Synchronization Lock: Protects the 'data' dictionary from concurrent access
data_lock = threading.Lock()

stopping_flag = False

current_jobs = []


def signal_handler(sig, frame):
    global stopping_flag
    # Use the lock when modifying a shared global variable
    with data_lock:
        if stopping_flag:
            print("\nForce Exiting...")
            cleanup_subprocess()
            os._exit(1)
        else:
            stopping_flag = True


signal.signal(signal.SIGINT, signal_handler)


@atexit.register
def cleanup_subprocess():
    for curjob in current_jobs:
        process = curjob.get('process')
        if process and process.poll() is None:  # Check if process is running
            print("Terminating subprocess...")
            process.terminate()
            try:
                process.wait(timeout=5)  # Give it some time to terminate
            except subprocess.TimeoutExpired:
                print("Subprocess did not terminate gracefully, killing...")
                process.kill()


@atexit.register
def print_all_errors():
    for uid, job in data.items():
        if job.get("status") == 'error':
            print(f'Job {uid} failed due to :')
            print(f'  {job.get("error", "Unknown")}')


data = load_json(DATA_FILE_PATH)

# Remove old data
print("Initiating data cleanup...")
jobs_to_delete = []
flags = ['stop.flag']
for flag in flags:
    try:
        os.remove(flag)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Unhandled error removing {flag}: {e}")

# Ensure safe access to shared data structure using the lock
with data_lock:
    for uid, job in data.items():
        status = job.get("status")

        # 1. Remove finished jobs
        if status in ["encoded", "copied"]:
            jobs_to_delete.append(uid)

        # 2. Reset jobs interrupted to 'not_started'
        elif status == "getting_frames":
            print(f"Resetting interrupted job {
                  uid} ({job.get('name', 'N/A')}) to 'not_started'.")
            job["status"] = "not_started"
        elif status == "encoding":
            print(f"Resetting interrupted job {
                  uid} ({job.get('name', 'N/A')}) to 'ready_to_encode'.")
            job["status"] = "ready_to_encode"
            try:
                os.remove(job['encoded_file'])
            except Exception as e:
                print(f'Failed to remove due to error: {e}')
                pass

        # 3. Keep jobs that are ready to encode (frame count is already done)
        elif status == "ready_to_encode":
            print(f"Job {uid} is 'ready_to_encode' and will be prioritized.")

        # 4. Report error jobs
        elif status == "error":
            joberror = job.get('error', 'Unknown')
            print(f"Job {uid} is in 'error' state. Error: {joberror}")
            jobaction = input(
                'Reset/delete/ignore job? (R/d/i): ').strip().lower()
            if jobaction in ['r', '']:
                if job.get('frames', None):
                    job['status'] = 'ready_to_encode'
                    try:
                        os.remove(job['encoded_file'])
                    except Exception as e:
                        print(f'Failed to remove due to error: {e}')
                        pass
                else:
                    job['status'] = 'not_started'
                    job['error'] = ''
            elif jobaction == 'd':
                jobs_to_delete.append(uid)
            elif jobaction != 'i':
                print('Unknown action. Ignoring.')

    # Perform the deletion outside the iteration
    for uid in jobs_to_delete:
        del data[uid]
        print(f"Removed completed job {uid}.")

print("Data cleanup complete.")


try:
    while True:

        # 🛑 PRIMARY EXIT CONDITION CHECK 🛑
        with data_lock:
            if os.path.exists('stop.flag'):
                if not stopping_flag:
                    print('Stopping flag enabled')
                    print(current_jobs)
                stopping_flag = True
            else:
                if stopping_flag:
                    print('Stopping flag disabled')
                stopping_flag = False
            if stopping_flag and not current_jobs:
                print("Graceful stop complete. All jobs finished. Exiting...")
                save_json(DATA_FILE_PATH, data)
                break  # Exit the while loop

        # == Load/Save Data ==
        for item in os.listdir('.'):
            if os.path.isfile(item) and re.fullmatch(r"input-\d+\.json", item):
                inputdata = load_json(Path(item))

                with data_lock:
                    nextuid = max((int(i) for i in data.keys()), default=0) + 1
                    for newjob in inputdata:
                        data[str(nextuid)] = newjob
                        nextuid += 1

                try:
                    print(f"REMOVING {item}")
                    os.remove(item)
                except Exception as e:
                    print(f'Failed to remove {item} due to {e}')

        # -- Save Main Data --
        with data_lock:
            save_json(DATA_FILE_PATH, data)

        # == Current Job Counts ==
        currentencodejobs = 0
        currentframecountjobs = 0
        for currentjob in current_jobs:
            if currentjob['type'] == 'encode':
                currentencodejobs += 1
            elif currentjob['type'] == 'framecount':
                currentframecountjobs += 1

        # == Look at current jobs (Cleanup) ==
        jobs_to_remove = [
            t for t in current_jobs
            if t["type"] == "encode"
            and not t["thread"].is_alive()
        ]
        for job in jobs_to_remove:
            job_uid = job["uid"]
            with data_lock:
                cur_status = data[job_uid]["status"]
                if cur_status.lower() != "error":
                    data[job_uid]["status"] = "encoded"
            current_jobs.remove(job)

        # == Create Jobs ==
        with data_lock:
            can_create_new_jobs = not stopping_flag

        if can_create_new_jobs:
            free_frame_count_jobs = max(
                0, maxframecountjobs - currentframecountjobs)
            available_frame_count_job_uids = jc.get_frame_count_jobs(
                data, data_lock, free_frame_count_jobs)
            for fc_job_uid in available_frame_count_job_uids:
                jc.create_frame_count_job(
                    fc_job_uid, data, data_lock, current_jobs
                )

            free_encode_jobs = max(
                0, maxencodejobs - currentencodejobs)
            available_encode_job_uids = jc.get_encode_jobs(
                data, data_lock, free_encode_jobs
            )
            for encode_job_uid in available_encode_job_uids:
                jc.create_encode_job(
                    encode_job_uid, data, data_lock, current_jobs
                )

        time.sleep(0.5)


except Exception as e:
    # Catch any unexpected exceptions
    print(f"\nAn unexpected error occurred: {e}")
