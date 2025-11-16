# Todo...

There is still lots to add. If there are any features you think should be added, feel free to make an issue.

- [ ] Add mode just to copy to correct names (encode quality original)
- [ ] Add restart flag for restarting daemon
- [ ] Add flag to clear finished jobs / series

- [ ] input.py
    - [ ] MOVE TO TUI
    - [ ] Allow custom output file name formats
    - [ ] Fix ctrl+c throwing 20 lines of error
- [ ] status.py
    - [x] Consider moving to TUI frontend such as textualize which would allow it to run as webpage.
    - [ ] Running status or input should trigger daemon to start.

- [ ] tui.py
    - [ ] Add input
    - [ ] Add config and manual pages
    - [ ] Allow reorganising of jobs

- [ ] compression script
    - [ ] Warn if output > input

- [ ] Prompt user for missing config.json & .env values when initially running input.py.
- [ ] Allow editing of current jobs.
- [ ] `scp` jobs for automatically moving files to a different device.
