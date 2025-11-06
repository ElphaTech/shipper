# shipper
**shipper** is a utility with the purpose of making re-encoding and compressing of movies and TV shows easier. While it is built with Plex in mind, it can be used for anything. It is comprised of a daemon which can be run in the background and also acts as a dashboard for current jobs as well as a input script to safely add new jobs to the queue.

Requirements
---
- ffmpeg


Installation & Usage
---
Move to the directory you keep your media in and clone the repository.
```sh
git clone https://github.com/ElphaTech/shipper.git
```

Enter the shipper directory.
```sh
cd shipper
```

Make and activate a virtual environment. Then install the requirements.
```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the daemon.
```sh
python daemon.py
```


In a **separate terminal** navigate to the shipper directory and run the following.

Make a .env file with your TMDB API key.
```env
TMDB_API_KEY=putyourkeyhere
```

Set input and output paths in config.json

Navigate up to your media directory. Activate the venv and run the input script.
```sh
source shipper/venv/bin/activate
python shipper/input.py
```


Features
---
- Input script with access to the TMDB api for automatically getting details such as:
    - Show name
    - Release year
    - Episode name
- Compression to different presets.
- Safe stopping of program with a `stop` file.
- Show progress of current jobs.

Todo
---
<details>
<summary>9/30 Complete</summary>

- [ ] Allow flag for shutdown on complete.
- [ ] Reorganise file structure to move functions to their own files.
    - [ ] daemon
    - [ ] input
    - [ ] status
- [ ] Improve input.py
    - [ ] Input directory
    - [ ] Output directory
    - [ ] Allow custom output file name formats
    - [ ] Fix ctrl+c throwing 20 lines of error
    - [ ] Finish tidying code
- [ ] Prompt user for missing config.json & .env values when initially running input.py.
- [ ] Separate daemon and status into distinct files to allow daemon to run fully as a background process.
    - [x] Create status script.
    - [ ] Consider moving to TUI frontend such as textualize which would allow it to run as webpage.
    - [ ] Remove all printing from daemon.
    - [ ] Change daemon printing to log file.
    - [ ] Allow user to let daemon begin on startup.
    - [ ] Running status or input should trigger daemon to start.
- [ ] Allow editing of current jobs.
- [ ] Add help/info command
- [ ] `scp` jobs for automatically moving files to a different device.
- [x] Improve error handling:
    - [x] Print errors on finish.
    - [x] Allow user to cancel job if failed last time.
    - [x] If error code, then show the meaning of the error code.
    - [x] Show errors on shipperd display.
- [x] Add a configuration file containing settings for:
    - [x] Compression presets
    - [x] Amount of jobs active at once
</details>

# config.json Parameters

`input_dir`: Full path to the directory where the input script will show files from.
`output_dir`: Full path to the directory where finished jobs should be saved to.
`storage_buffer`: The amount of GiB the program should leave free. Upon reaching this limit, it will not start any new jobs.
`job_limits`: The amount of each type of job that can happen at once. If your system is more powerful, you can increase these.
`quality_presets`: Preset quality values that you can choose between in the input program. For more information see the [FFmpeg docs](https://ffmpeg.org/ffmpeg-codecs.html)

# Plex file structure
```
/plexmedia/
├── Movies/
│   └── Name (Year) {ID}/
│       └── Name (Year) {ID}.ext
└── TVShows/
    └── Name (Year) {ID}/
        └── Season 00/
            └── Name (Year) - s00e00 - EpName.ext
```


