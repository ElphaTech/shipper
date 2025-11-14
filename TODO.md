# Todo...

There is still lots to add. If there are any features you think should be added, feel free to make an issue.

- [ ] Add mode just to copy to correct names (encode quality original)

- [x] Reorganise file structure to move functions to their own files.
    - [x] daemon
    - [x] input
    - [x] status

- [ ] input.py
    - [ ] Allow custom output file name formats
    - [ ] Fix ctrl+c throwing 20 lines of error
    - [ ] Potentially make part of status.py TUI
- [ ] status.py
    - [ ] Consider moving to TUI frontend such as textualize which would allow it to run as webpage.
    - [ ] Running status or input should trigger daemon to start.
- [x] daemon.py
    - [x] Integrate new compression integration
    - [x] Move all ffmpeg to using external functions

- [ ] compression script
    - [ ] Warn if output > input

- [ ] Prompt user for missing config.json & .env values when initially running input.py.
- [ ] Allow editing of current jobs.
- [ ] Add help/info command
- [ ] `scp` jobs for automatically moving files to a different device.
