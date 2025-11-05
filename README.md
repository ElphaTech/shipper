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
- [ ] Improve error handling:
    - [ ] Print errors on finish.
    - [x] Allow user to cancel job if failed last time.
    - [x] If error code, then show the meaning of the error code.
    - [x] Show errors on shipperd display.
- [ ] Allow flag for shutdown on complete.
- [ ] Reorganise file structure to move functions to their own files.
- [x] Add a configuration file containing settings for:
    - [ ] Input directory
    - [ ] Output directory
    - [ ] Allow custom output file name formats
    - [x] Compression presets
    - [x] Amount of jobs active at once
- [ ] Prompt user for missing config.json & .env values when initially running input.py.
- [ ] Separate daemon and status into distinct files to allow daemon to run fully as a background process.
    - [ ] Allow user to let daemon begin on startup.
    - [ ] Running status or input should trigger daemon to start.
- [ ] `scp` jobs for automatically moving files to a different device.

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


