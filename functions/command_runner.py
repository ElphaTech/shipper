import subprocess
import signal
import shlex
import os
from typing import Union, List


def run_terminal_command(command: Union[str, List[str]]) -> str:
    """
    Executes a terminal command and returns the combined stdout and stderr
    output as a single string.

    This function handles both string commands (which are split safely) 
    and list-of-string commands (the preferred secure method).

    Args:
        command: The command to execute, either as a space-separated string
                 (e.g., "ls -l /tmp") or a list of arguments (e.g., ["ls", "-l", "/tmp"]).

    Returns:
        A string containing the output of the command, or an error message
        if the command fails to execute.
    """

    # 1. Safely parse the command if it's provided as a string
    if isinstance(command, str):
        # shlex.split safely handles quotes and spaces in arguments
        command_list = shlex.split(command)
    elif isinstance(command, list):
        command_list = command
    else:
        return f"Error: Invalid command format. Expected string or list, got {type(command).__name__}."

    if not command_list:
        return "Error: Command list is empty."

    def set_sigint_ignore():
        """
        Sets the signal handler for SIGINT to ignore in the child process,
        preventing external interrupts from killing the running command.
        """
        # Only set if running on POSIX systems (e.g., Linux, macOS)
        if os.name == 'posix':
            signal.signal(signal.SIGINT, signal.SIG_IGN)

    try:
        # 2. Execute the command
        # capture_output=True collects stdout and stderr
        # text=True decodes the output as text (using the system default encoding)
        # check=False ensures that we don't raise an exception just because the command
        # returns a non-zero exit code (failure); we'll check the exit code manually.
        result = subprocess.run(
            command_list,
            capture_output=True,
            text=True,
            check=False,  # Allows us to handle the return code ourselves
            preexec_fn=set_sigint_ignore
        )

        # 3. Check the return code and format the output
        if result.returncode != 0:
            # If the command failed, return a specific error message including stderr
            return (
                f"Command failed with exit code {result.returncode}:\n"
                f"Command: {' '.join(command_list)}\n"
                f"--- Standard Error ---\n{result.stderr.strip()
                                           or 'No error output'}\n"
                f"--- Standard Output ---\n{result.stdout.strip()
                                            or 'No standard output'}"
            )
        else:
            # If successful, return the combined standard output
            # We prioritize stdout but include stderr if it exists (e.g., for warnings)
            output = result.stdout.strip()
            if result.stderr:
                output += f"\n\n[Warning: The command also produced the following standard error (stderr) output]:\n{
                    result.stderr.strip()}"

            return output if output else "Command executed successfully, but produced no output."

    except FileNotFoundError:
        # This occurs if the executable itself (the first item in the list) is not found
        return f"Error: Command executable not found: '{command_list[0]}'. Check your PATH."
    except Exception as e:
        # Catch any unexpected errors during execution setup
        return f"Unexpected error during command execution: {e}"


def run_ffmpeg_encode(
    uid,
    data,
    data_lock,
    quality,
    audio_map,
    subtitle_map
):
    with data_lock:
        cmd = f"""
ffmpeg -hide_banner -loglevel info -stats -progress pipe:1
-i {data[uid]["input_file"]}
-map 0:v:0
{audio_map}
{subtitle_map}
-c:v libx265
-preset {quality["preset"]}
-crf {quality["crf"]}
-x265-params "aq-mode={quality['aq_mode']}"
-c:a aac -b:a {quality['bitrate']}
-c:s copy
{data[uid]["encoded_file"]}
"""
    shlex.split(cmd)
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )

    while True:
        line = process.stderr.readline()
        if not line and process.poll() is not None:
            break

        if line and line.startswith("frame="):
            try:
                curframe = int(line.split("=")[1])
                with data_lock:
                    data[uid]["current_frame"] = curframe

            except ValueError:
                pass

    # Wait for the process to fully finish and get the return code
    return process.wait()


if __name__ == "__main__":
    print("--- Example 1 (Successful Command) ---")
    print(run_terminal_command("echo Hello World"))
    print("--- Example 2 (Command with arguments) ---")
    print(run_terminal_command("ls -a /"))
    print("--- Example 3 (Failing Command) ---")
    print(run_terminal_command("cat non_existent_file.txt"))
    print("--- Example 4 (Command without output)")
    print(run_terminal_command("touch nothing"))
