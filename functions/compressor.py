# == PLAN ==
# [x] Checks if input and output files exists
# [x] Checks valid preset & gets preset values
# [x] Check enough disk space
# [ ] If english audio exists, use it
# [ ] If english subs exist, use them
# [ ] Run ffmpeg
# [ ] Warn if output > input
from pathlib import Path

from config import load_config
import disk_stats as ds

CONFIG = load_config()


def create_ffmpeg_cmd(input_path: str, output_path: str, quality_key: str):
    """
    Function to start compression of a video.
    Returns a process when working.
    Returns a string if error.
    """
    # Check input exists and output does not
    if not Path(input_path).exists():
        error_message = "Input file does not exist (compressor)"
        print(error_message)
        return error_message
    if Path(output_path).exists():
        error_message = "Output file already exists (compressor)"
        print(error_message)
        return error_message

    # Safely load quality config
    try:
        quality = CONFIG.quality_presets[quality_key]
    except Exception as e:
        error_message = f"Failed to get quality (compressor): {e}"
        print(error_message)
        return error_message

    # Check free space
    buffer = ds.gib_to_bytes(CONFIG.buffer)
    if not ds.check_enough_space(input_path, buffer):
        error_message = f"Not enough free space on disk (compressor)"
        print(error_message)
        return error_message


if __name__ == '__main__':
    pass
