import atexit
import os
import re
import signal
import subprocess
import threading
import time
from pathlib import Path

from functions.config import PROJECT_ROOT, load_config
from functions.file_handler import load_json, save_json
import functions.logger

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

# GRACEFUL STOP FLAG
stopping_flag = False

currentjobs = []


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


# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)


@atexit.register
def cleanup_subprocess():
    for curjob in currentjobs:
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


def get_frame_count(file_path: str) -> int | str:
    """
    Return total frame count of a video using ffprobe,
    or an error string on failure.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found — {file_path}"

    def set_sigint_ignore():
        """
        Sets the signal handler for SIGINT to ignore in the child.
        """
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=nb_frames",
                "-of", "default=nokey=1:noprint_wrappers=1", file_path
            ],
            capture_output=True, text=True, check=True,
            preexec_fn=set_sigint_ignore
        )
        # Tries to get frame count from stream metadata
        try:
            frames = int(result.stdout.strip())
            if frames > 0:
                return frames
        except ValueError:
            pass  # Fallback to counting packets if stream data is missing

        # Second attempt: count packets
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "frame=pkt_pts_time",
                "-select_streams", "v:0",
                "-of", "csv=p=0", file_path
            ],
            capture_output=True, text=True, check=True,
            preexec_fn=set_sigint_ignore
        )
        lines = result.stdout.count('\n')
        if not lines:
            return f"Error: Failed to retrieve frame data from {file_path}"
        return lines

    except subprocess.CalledProcessError as e:
        return f"Error running ffprobe: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


def encode_file(infile, outfile, quality):
    pass


def threaded_frame_count(uid, input_file, data, currentjob_list):
    """Runs frame count and updates shared data structure upon completion."""
    frames_or_error = get_frame_count(input_file)

    # Use the lock to safely update the shared 'data' dictionary and remove job
    with data_lock:
        if type(frames_or_error) is int:
            # Success
            # Store total frames in 'data'
            data[uid]["frames"] = frames_or_error
            data[uid]["status"] = "ready_to_encode"  # Transition to ready
        else:
            # Failure
            data[uid]["status"] = 'error'
            data[uid]["error"] = str(frames_or_error)

        # Remove the framecount job from the currentjobs list
        job_to_remove = next((
            j for j in currentjob_list
            if j["uid"] == uid and j["type"] == "framecount"), None
        )
        if job_to_remove:
            currentjob_list.remove(job_to_remove)


def read_progress(proc, job):
    frame_lines = [
        line for line in proc.stdout if line.startswith("frame=")
    ]

    for line in frame_lines:
        try:
            curframe = int(line.split("=")[1])
            job["curframe"] = curframe
            with data_lock:
                data[job['uid']]["current_frame"] = curframe

        except ValueError:
            pass

    proc.stdout.close()


data = load_json(DATA_FILE_PATH)

# Remove old data
print("Initiating data cleanup...")
jobs_to_delete = []
try:
    os.remove('stop')
except FileNotFoundError:
    pass
except Exception as e:
    print(f"Unhandled error removing 'stop': {e}")

# Ensure safe access to shared data structure using the lock
with data_lock:
    for uid, job in data.items():
        status = job.get("status")

        # 1. Remove finished jobs
        if status in ["encoded", "copied"]:
            jobs_to_delete.append(uid)

        # 2. Reset jobs interrupted to 'notstarted'
        elif status == "getting_frames":
            print(f"Resetting interrupted job {
                  uid} ({job.get('name', 'N/A')}) to 'notstarted'.")
            job["status"] = "notstarted"
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
                    job['status'] = 'notstarted'
            if jobaction == 'd':
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
            if os.path.exists('stop'):
                stopping_flag = True
            if os.path.exists('unstop'):
                stopping_flag = False
                os.remove('stop')
                os.remove('unstop')
            if stopping_flag and not currentjobs:
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
        for currentjob in currentjobs:
            if currentjob['type'] == 'encode':
                currentencodejobs += 1
            elif currentjob['type'] == 'framecount':
                currentframecountjobs += 1

        # == Look at current jobs (Cleanup) ==
        for currentjob in currentjobs:
            if currentjob['type'] == 'encode':
                uid = currentjob['uid']
                try:
                    exitcode = currentjob['process'].poll()
                except Exception as e:
                    print(f'bro its so jover: {e}')

                if exitcode is not None:
                    # Safely update shared 'data' dictionary
                    with data_lock:
                        if exitcode == 0:
                            data[uid]['status'] = 'encoded'
                            currentjobs.remove(currentjob)
                        else:
                            exitcodes = {
                                2: "Input directory not given. This shouldn't be possible.",
                                3: "Output directory not given. This shouldn't be possible.",
                                7: "Input file does not exist. Please either stop the daemon and fix the path or remove the job and readd it with the input script.",
                                4: "Invalid quality setting. This shouldn't be possible if you used the input script.",
                                5: "Disk space too low. Please clear space.",
                                6: "Unknown error. Normally due to ffmpeg being killed or ffmpeg failing."
                            }
                            data[uid]["status"] = 'error'
                            data[uid]["error"] = f'{exitcode}: {
                                exitcodes[exitcode]}'
                            currentjobs.remove(currentjob)
            # Framecount jobs are cleaned up within 'threaded_frame_count'

        # == Create Jobs ==
        with data_lock:
            can_create_new_jobs = not stopping_flag

        if can_create_new_jobs:

            # 1. Start Frame Count Jobs (if capacity is available)
            if currentframecountjobs < maxframecountjobs:
                # Check for jobs that need frame counting (notstarted)
                uid_to_count = None
                with data_lock:
                    uid_to_count = next((
                        k for k, v in data.items()
                        if v.get("status") == "notstarted"), None
                    )

                if uid_to_count:
                    # Update status and launch thread (outside lock since 'data' is accessed again)
                    with data_lock:
                        data[uid_to_count]["status"] = 'getting_frames'

                        # Add job to currentjobs list
                        currentjobs.append({
                            "type": "framecount",
                            "uid": uid_to_count,
                            "thread": None  # Placeholder for thread object if needed
                        })

                        print(f'Starting frame count for UID {uid_to_count}')

                        t = threading.Thread(
                            target=threaded_frame_count,
                            args=(
                                uid_to_count,
                                data[uid_to_count]["input_file"],
                                data,
                                currentjobs  # Pass currentjobs list to remove self on completion
                            ),
                            daemon=True
                        )
                        t.start()
                        # Store the thread object
                        currentjobs[-1]["thread"] = t

            # 2. Start Encoding Jobs (if capacity is available)
            if currentencodejobs < maxencodejobs:
                # Check for jobs that are ready to encode (counting complete)
                uid = None
                with data_lock:
                    uid = next((
                        k for k, v in data.items() if v.get("status") == "ready_to_encode"),
                        None)

                if uid:
                    # Total frames is now stored in data[uid]["frames"]
                    frames = data[uid]["frames"]

                    with data_lock:
                        # Update status and launch subprocess
                        data[uid]["status"] = 'encoding'
                        data[uid]["job_start_time"] = int(time.time())
                        data[uid]["encode_start_time"] = int(time.time())

                        currentjobs.append({
                            "type": "encode",
                            "uid": uid,
                            "frames": frames,
                            "curframe": 0,
                            "process": None
                        })

                    try:
                        os.makedirs(
                            os.path.dirname(data[uid]["encoded_file"]),
                            exist_ok=True)
                        currentjobs[-1]["process"] = subprocess.Popen([
                            "./compress_file.sh",
                            data[uid]["input_file"],
                            data[uid]["encoded_file"],
                            data[uid]["quality"]
                        ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            text=True,
                            bufsize=1
                        )
                        threading.Thread(
                            target=read_progress,
                            args=(currentjobs[-1]["process"], currentjobs[-1]),
                            daemon=True
                        ).start()
                    except Exception as e:
                        with data_lock:
                            data[uid]["status"] = 'error'
                            data[uid]["error"] = str(e)
                    finally:
                        pass

        time.sleep(0.5)  # Add a small sleep to prevent 100% CPU usage


except Exception as e:
    # Catch any unexpected exceptions
    print(f"\nAn unexpected error occurred: {e}")
    print(f"\nAn unexpected error occurred: {e}")
