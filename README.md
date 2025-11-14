# shipper
**shipper** is a utility with the purpose of making re-encoding and compressing of movies and TV shows easier. While it is built with Plex in mind, it can be used for anything. It is comprised of a daemon which can be run in the background and also acts as a dashboard for current jobs as well as a input script to safely add new jobs to the queue.

If you try to use it and have any problems or questions feel free to make a issue and I'll get back to you asap.

> [!WARNING]
> This repository is very much **work in progress**. Most commits will break previous versions. It is likely that many features will only partly work or not work at all.

Requirements
---
- FFmpeg


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


