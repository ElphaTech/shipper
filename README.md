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

Enter the shipper directory and run the daemon.
```sh
cd shipper
python shipperd.py
```


To use the input script a few libraries are needed. In a **seperate terminal** navigate to the shipper directory and run the following.

Make and activate a virtual environment. Then install the requirements.
```sh
python -m venv venv
source venv/bin/activate
pip install requirements.txt
```

Make a .env file with your TMDB API key.
```env
TMDB_API_KEY=putyourkeyhere
```

Run the input script.
```sh
python shipper_input.py
```


Features
---
- Input script with access to the TMDB api for automatically getting details such as:
    - Show name
    - Release year
    - Episode name
- Compression to different presets.
- Safe stopping of program with a `stop` file.

Todo
---
- [ ] Improve error handling:
    - [ ] Allow user to cancel job if failed last time.
    - [ ] Print errors on finish.
    - [ ] If error code, then show the meaning of the error code.
    - [ ] Show errors on shipperd display.
- [ ] Allow flag for shutdown on complete.
- [ ] Reorganise file structure to move functions to their own files.
- [ ] Add a configuration file containing settings for:
    - [ ] Input directory
    - [ ] Output directory
    - [ ] Compression presets
    - [ ] Amount of jobs active at once
    - [ ] Allow custom output formats
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


