import pprint
import time
import re

try:
    from functions.config import PROJECT_ROOT, load_config
    from functions.disk_stats import get_disk_metrics, print_disk_usage
    from functions.file_handler import load_json
except Exception:
    from config import PROJECT_ROOT, load_config
    from disk_stats import get_disk_metrics, print_disk_usage
    from file_handler import load_json

CONFIG = load_config()
DATA_FILE_PATH = PROJECT_ROOT / "data.json"
STOPPING_FLAG_FILE_PATH = PROJECT_ROOT / "stop.flag"

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


def get_pct(job):
    total_frames = job.get("frames", 0)
    current_frames = job.get("current_frame", 0)
    if total_frames > 0:
        if current_frames == 0:
            return 0
        else:
            return (current_frames / total_frames) * 100
    return 0


def get_pct_str(job):
    pct = get_pct(job)
    if job["status"] == "encoding":
        return f"{pct:5.1f}%"
    return ""


def get_eta(job):
    now = int(time.time())
    if (job['status'] == "encoding"
        and job.get("encode_start_time")
        and job["encode_start_time"] != now
        ):
        elapsed = now - job["encode_start_time"]
        pct = get_pct(job)
        # pct+0.01 to avoid div/0
        total_est = elapsed / ((pct+0.01) / 100)
        return format_time(total_est - elapsed)
    return ''


def parse_episode_code(episode_code: str):
    """Return (season, episode) numbers from 'SxxExx', or (0, 0) if invalid."""
    match = re.search(r"[Ss](\d+)[Ee](\d+)", episode_code or "")
    if not match:
        return 0, 0
    return map(int, match.groups())


def get_data_table(
        data: dict, shown_columns: list = CONFIG.textual_columns) -> dict:
    output_table = {}

    for uid, job in data.items():
        output_table[uid] = {}
        for column in shown_columns:
            if column == 'percentage':
                output_table[uid]['percentage'] = get_pct_str(job)
            elif column == 'eta':
                output_table[uid]['eta'] = get_eta(job)
            elif column in job.keys():
                output_table[uid][column] = job[column]
    return output_table


def get_overview_data_table(
        data: dict, shown_columns: list = CONFIG.textual_overview_columns) -> dict:
    input_table = get_data_table(data, [
        "name",
        "status",
        "percentage",
        "id",
    ])
    output_table = {}
    for uid, job in input_table.items():
        sn, ep = parse_episode_code(job["name"])
        job_id = f'{job["id"]}:{sn:02}'
        if job_id not in output_table.keys():
            output_table[job_id] = {
                "total": 0,
                "not_started": 0,
                "encoded": 0,
                "name": job["name"],
            }
        output_table[job_id]["total"] += 1
        if job["status"] == 'not_started':
            output_table[job_id]["not_started"] += 1
        elif job["status"] == "encoded":
            output_table[job_id]["encoded"] += 1
    for job_id in output_table:
        try:
            output_table[job_id]["progress"] = f'{
                output_table[job_id]["encoded"]}/{output_table[job_id]["total"]}'
            pct = output_table[job_id]["encoded"]/output_table[job_id]["total"]
            if pct == 0:
                output_table[job_id]["status"] = "Not Started"
            elif pct == 1:
                output_table[job_id]["status"] = "Complete"
            else:
                output_table[job_id]["status"] = "In Progress"
        except:
            raise Exception(output_table)

        try:
            del output_table[job_id]["total"]
            del output_table[job_id]["not_started"]
            del output_table[job_id]["encoded"]
        except:
            pass

    return output_table


if __name__ == "__main__":
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
    pprint.pprint(get_data_table(data))
