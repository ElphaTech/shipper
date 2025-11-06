"""
A small script to capture all print statements and also send them to a log.
"""
import logging
import builtins
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_ROOT / "shipper.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

_original_print = builtins.print


def custom_print(*args, sep=' ', end='\n', file=None, flush=False):
    """
    A wrapper for the built-in print function that also logs output to a file.
    """
    _original_print(*args, sep=sep, end=end, file=file, flush=flush)
    message = sep.join(map(str, args))
    logging.info(message)


builtins.print = custom_print

if __name__ == "__main__":
    print("This will print to the console AND the file.")
    print(123, "and", "a list", [1, 2, 3])
