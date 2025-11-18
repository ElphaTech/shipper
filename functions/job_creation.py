import threading
import os
import signal
import subprocess
import time
from pathlib import Path

from .compressor import encode_video


def get_frame_count_jobs(data, data_lock, max_jobs):
    with data_lock:
        uids = [
            k for k, v in data.items()
            if v.get("status") == "not_started"
        ][:max_jobs]
    return uids


def get_encode_jobs(data, data_lock, max_jobs):
    with data_lock:
        uids = [
            k for k, v in data.items()
            if v.get("status") == "ready_to_encode"
        ][:max_jobs]
    return uids


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


def threaded_frame_count(uid, data, data_lock, current_jobs):
    """Runs frame count and updates shared data structure upon completion."""
    input_file = data[uid]['input_file']
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

        # Remove the framecount job from the current_jobs list
        job_to_remove = next((
            j for j in current_jobs
            if j["uid"] == uid and j["type"] == "framecount"), None
        )
        if job_to_remove:
            current_jobs.remove(job_to_remove)


def create_frame_count_job(uid, data, data_lock, current_jobs):
    with data_lock:
        data[uid]["status"] = 'getting_frames'

        # Add job to current_jobs list
        current_jobs.append({
            "type": "framecount",
            "uid": uid,
            "thread": None  # Placeholder for thread object if needed
        })

        print(f'Starting frame count for UID {uid}')

        t = threading.Thread(
            target=threaded_frame_count,
            args=(
                uid,
                data,
                data_lock,
                current_jobs
            ),
            daemon=True
        )
        t.start()
        # Store the thread object
        current_jobs[-1]["thread"] = t


def read_progress(proc, job, data, data_lock):
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


def create_encode_job(uid, data, data_lock, current_jobs):
    with data_lock:
        data[uid]["status"] = 'encoding'
        data[uid]["job_start_time"] = int(time.time())
        data[uid]["encode_start_time"] = int(time.time())

        # Create output folder
        Path(data[uid]["encoded_file"]).parent.mkdir(
            parents=True, exist_ok=True)

        # Add job to current_jobs list
        current_jobs.append({
            "type": "encode",
            "uid": uid,
            "thread": None
        })

        print(f'Starting encoding for UID {uid}')

        t = threading.Thread(
            target=encode_video,
            args=(
                uid,
                data,
                data_lock
            ),
            daemon=True
        )
        t.start()
        print(t)
        current_jobs[-1]["thread"] = t
