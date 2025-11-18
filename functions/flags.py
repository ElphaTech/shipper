'''
Functions for finding, adding and removing flags.
All flags are empty files with a .flag suffix.
They are always found in the root directory of the project.
'''

from pathlib import Path

from .config import load_config, PROJECT_ROOT


def flag_name_to_path(flag_name: str) -> Path:
    '''
    A helper function to get the path of a flag_name.
    '''
    return PROJECT_ROOT / f"{flag_name}.flag"


def path_to_flag_name(path: Path) -> str:
    '''
    A helper function to get the flag_name of a path.
    '''
    return path.stem


def check_flag(flag_name: str) -> bool:
    '''
    A function to check if a flag exists.
    Takes in a flag name such as 'stop' or 'restart'.
    Returns a boolean, true if the flag file exists, otherwise false.
    '''
    return flag_name_to_path(flag_name).exists()


def get_flag_creation_time(flag_name: str) -> float | bool:
    '''
    A function to get the last modified time of a flag file.
    Takes in a flag name such as 'stop' or 'restart'.
    Returns a float with the seconds since the epoch if the file exists.
    Returns None if the file does not exist.
    '''
    path = flag_name_to_path(flag_name)
    return path.stat().st_mtime if path.is_file() else None


def create_flag(flag_name: str):
    '''
    A function that creates a flag file.
    Takes in a flag name such as 'stop' or 'restart'.
    Does not return anything.
    '''
    path = flag_name_to_path(flag_name)
    path.touch(exist_ok=True)


def remove_flag(flag_name: str):
    '''
    A function that deletes a flag file.
    Takes in a flag name such as 'stop' or 'restart'.
    Does not return anything.
    '''
    path = flag_name_to_path(flag_name)
    if path.exists():
        path.unlink()


def get_active_flags() -> list:
    '''
    A function that returns the names of all existing flag files.
    Takes no arguments.
    Returns a list of flag names as strings.
    '''
    return [
        p.stem
        for p in PROJECT_ROOT.glob("*.flag")
        if p.is_file()
    ]


# Checks to test all functions
if __name__ == "__main__":
    test_name = "testflagfortesting"

    print("Creating flag…")
    create_flag(test_name)
    print("Exists:", check_flag(test_name))
    print("mtime:", get_flag_creation_time(test_name))

    print("\nActive flags:", get_active_flags())

    print("\nRemoving flag…")
    remove_flag(test_name)
    print("Exists after removal:", check_flag(test_name))

    print("\nActive flags:", get_active_flags())
