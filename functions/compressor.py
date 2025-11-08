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
from command_runner import run_terminal_command, run_ffmpeg_encode

CONFIG = load_config()


def verify_video_ready(input_path: str, output_path: str, quality_key: str):
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

    # Check free space
    buffer = ds.gib_to_bytes(CONFIG.buffer)
    if not ds.check_enough_space(input_path, buffer):
        error_message = "Not enough free space on disk (compressor)"
        print(error_message)
        return error_message

    # Safely load quality config
    try:
        return CONFIG.quality_presets[quality_key]
    except Exception as e:
        error_message = f"Failed to get quality (compressor): {e}"
        print(error_message)
        return error_message


def encode_video(uid, data, data_lock):
    with data_lock:
        input_path = data[uid]["input_file"]
        output_path = data[uid]["encoded_file"]
        quality_key = data[uid]["quality"]

    quality = verify_video_ready(input_path, output_path, quality_key)

    # get audio
    if run_terminal_command(f'''ffprobe -v error -select_streams a
-show_entries stream_tags=language -of default=
noprint_wrappers=1:nokey=1 {input_path}''') == 'eng':
        audio_map = "-map 0:a:m:language:eng"
    else:
        audio_map = "-map 0:a:0"

    # get subtitles
    if run_terminal_command(f'''ffprobe -v error -select_streams s
-show_entries stream_tags=language -of default=
noprint_wrappers=1:nokey=1 {input_path}''') == 'eng':
        subtitle_map = "-map 0:s:m:language:eng"
    else:
        subtitle_map = "-map 0:s:0"

    return run_ffmpeg_encode(
        uid,
        data,
        data_lock,
        quality,
        audio_map,
        subtitle_map
    )


if __name__ == '__main__':
    pass
