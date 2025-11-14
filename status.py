import os
import time

from functions.config import PROJECT_ROOT, load_config
from functions.disk_stats import get_disk_metrics, print_disk_usage
from functions.file_handler import load_json

CONFIG = load_config()
DATA_FILE_PATH = PROJECT_ROOT / "data.json"
STOPPING_FLAG_FILE_PATH = PROJECT_ROOT / "stop.flag"

# Loooop the following
# 1) Load data.json
# 2) Process and print data.json

if not DATA_FILE_PATH.exists():
    print("Error: data.json file missing.")
    print("Please make sure that the daemon is currently running.")
    print(f"Tried to find data.json at {DATA_FILE_PATH}")
    exit()


def get_progress_stats(progress: int, total: int, width: int
                       ) -> (float, str):
    """
    A function that takes a current amount, a total amount and
    the width of a progress bar.
    It returns a percentage as a float and progress bar.
    If total is 0, then it uses 0%.
    """
    if total == 0:
        percentage = 0
    else:
        percentage = progress / total

    filled_characters = int(percentage * width)
    filled_bar = '#' * filled_characters
    empty_bar = ' ' * (width - filled_characters)
    progress_bar = f"[{filled_bar}{empty_bar}]"
    return (
        percentage,
        progress_bar
    )


def format_time(seconds: int) -> str:
    """
    Formats seconds into a string of either
    seconds, minutes and hours.
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"


def show_status(data):
    now = int(time.time())

    header = f"{'ID':<5} | {'Name':<25} | {
        'Status':<18} | {'Progress':<12} | {'ETA':<8}"
    print(header)
    print("-" * len(header))

    for uid, job in data.items():
        status = job["status"]
        total_frames = job.get("frames", 0)
        current_frames = job.get("current_frame", 0)
        progress = ""
        eta = ""

        if status == "encoding" and total_frames > 0:
            frames = job["frames"]

            if current_frames == 0:
                pct = 0.1
            else:
                pct = (current_frames / frames) * 100
            progress = f"{pct:5.1f}%"

            if (job.get("encode_start_time")
                    and job["encode_start_time"] != now):
                elapsed = now - job["encode_start_time"]
                total_est = elapsed / (pct / 100)
                eta = format_time(total_est - elapsed)

        name_len = 25
        if job.get("type", "movie") == "tv":
            first, rest = job['name'].split(' - ', 1)
            short = (first[:(name_len - 12)] +
                     "...") if len(first) > name_len else first
            print_name = f"{short} - {rest}"
        else:
            print_name = job["name"][:name_len].rjust(name_len)
        if status != 'error':
            print(f"{uid:>5} | {print_name} | {
                status:<18} | {progress:<12} | {eta:<8}")
        else:
            if data[uid].get('error'):
                print(f"{uid:>5} | {print_name} | {
                    status:<18}: {data[uid]['error']:<24}")
            else:
                print(f"{uid:>5} | {short} - {rest} | {
                    status:<18}: Unknown")


if __name__ == "__main__":
    while True:
        os.system('clear')

        # Show stopping flag if applicable
        stopping_flag = STOPPING_FLAG_FILE_PATH.exists()
        if stopping_flag:
            print("Daemon will stop when all jobs are complete.")
            print("To reverse this, create a file called \"unstop\"")

        # Show disk usage stats
        print_disk_usage(
            *get_disk_metrics(), 20
        )

        # Show main data
        data = load_json(DATA_FILE_PATH)
        show_status(data)

        # pause to stop crazy usage
        time.sleep(0.5)
