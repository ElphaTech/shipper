'''
Functions for finding, adding and removing flags.
All flags are empty files with a .flag suffix.
They are always found in the root directory of the project.
'''

from pathlib import Path

from .config import load_config, PROJECT_ROOT


def check_flag(flag_name: str) -> bool:
    '''
    A function to check if a flag exists.
    Takes in a flag name such as 'stop' or 'restart'.
    Returns a boolean, true if the flag file exists, otherwise false.
    '''


def get_flag_creation_time(flag_name: str) -> float | bool:
    '''
    A function to get the last modified time of a flag file.
    Takes in a flag name such as 'stop' or 'restart'.
    Returns a float with the seconds since the epoch if the file exists.
    Returns false if the file does not exist.
    '''


def create_flag(flag_name: str):
    '''
    A function that creates a flag file.
    Takes in a flag name such as 'stop' or 'restart'.
    Does not return anything.
    '''


def remove_flag(flag_name: str):
    '''
    A function that deletes a flag file.
    Takes in a flag name such as 'stop' or 'restart'.
    Does not return anything.
    '''


def get_active_flags() -> list:
    '''
    A function that returns the names of all existing flag files.
    Takes no arguments.
    Returns a list of flag names as strings.
    '''
