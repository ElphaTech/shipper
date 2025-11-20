# Flags
All flags are empty files with a .flag suffix.
They are always found in the root directory of the project.

> [!WARNING]
> Flags are cleared upon starting the daemon. Therefore all permanent settings should be stored in `config.json`.

# All flags
To get a list of all flags, get the `ALL_FLAGS` variable from `functions/flags.py`.
Here is an explanation of what each one does.
- `start_daemon`: Starts a daemon process if none currently exist. Be warned that it does take >5 seconds to take effect.
- `safe_stop_daemon`: Safely stops the currently running daemon process by making it wait until it completes all current jobs and then quitting.
- `quick_stop_daemon`: Stops daemon by getting it to immediately kill itself. WARNING: THIS WILL CAUSE ALL CURRENTLY RUNNING JOBS TO FAIL.

# Functions
`functions/flags.py` contains some helpful functions to assist with flags. Here is each one.


## Helper functions
These are not really meant to be used outside of the `flags.py` script but are just there to make other functions easier to read.

`flag_name_to_path(flag_name: str) -> Path`
A helper function to get the path of a flag_name.


`path_to_flag_name(path: Path) -> str`
A helper function to get the flag_name of a path.


## Main functions
These functions are all meant to be used outside of the `flags.py` script.

`check_flag(flag_name: str) -> bool`
A function to check if a flag exists.
Takes in a flag name such as 'stop' or 'restart'.
Returns a boolean, true if the flag file exists, otherwise false.


`get_flag_creation_time(flag_name: str) -> float | bool`
A function to get the last modified time of a flag file.
Takes in a flag name such as 'stop' or 'restart'.
Returns a float with the seconds since the epoch if the file exists.
Returns None if the file does not exist.


`create_flag(flag_name: str)`
A function that creates a flag file.
Takes in a flag name such as 'stop' or 'restart'.
Does not return anything.


`remove_flag(flag_name: str)`
A function that deletes a flag file.
Takes in a flag name such as 'stop' or 'restart'.
Does not return anything.


`get_active_flags() -> list`
A function that returns the names of all existing flag files.
Takes no arguments.
Returns a list of flag names as strings.
