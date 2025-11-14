import survey
import os
import re
import tmdbsimple as tmdb
from copy import deepcopy
import time
import json
from functions.tmdb_client import get_media_info, get_episode_title
from functions.config import load_config
from pathlib import Path

CONFIG = load_config()

tmdb.API_KEY = CONFIG.tmdb_api_key
tmdb.REQUESTS_TIMEOUT = 5

INPUT_DIR = CONFIG.input_dir
OUTPUT_DIR = CONFIG.output_dir
print(INPUT_DIR)

qualities = tuple(CONFIG.quality_presets.keys())

output = []
defaultjob = {
    "id": "",
    "name": "",
    "year": "",
    "quality": "",
    "type": "",
    "status": "notstarted",
    "input_file": "",
    "encoded_file": "",
    "before_size": 0,
    "after_size": 0,
    "percentage_encoded": 0,
    "percentage_copied": 0,
    "job_start_time": 0,
    "encode_start_time": 0,
    "encode_end_time": 0,
    "copy_start_time": 0,
    "copy_end_time": 0,
    "job_end_time": 0,
    "current_frames": 0
}


def select_and_list_videos(input_dir: Path = INPUT_DIR):
    """
    Selects and lists video files and folders from a specified input directory
    using the pathlib module.
    """
    # 1. List entries in INPUT_DIR
    entries = []
    for entry in input_dir.iterdir():
        # Exclude hidden files/folders (starting with '.')
        if entry.name.startswith('.'):
            continue

        # Check for directories or files with video extensions
        is_video = entry.suffix.lower() in ('.mkv', '.mp4')
        if entry.is_dir() or is_video:
            # Append a trailing '/' for directories in the display list
            display_name = entry.name + '/' if entry.is_dir() else entry.name
            # Store (display_name, full_path)
            entries.append((display_name, entry))

    # Sort the display names for presentation
    entries.sort(key=lambda x: x[0])

    # Extract just the display names for the survey selection
    display_entries = [d for d, p in entries]

    # Map back from display name to the full Path object after selection
    path_map = {d: p for d, p in entries}

    # 2. Survey selection
    selection = survey.routines.basket(
        f'Select folders/files in {input_dir}:',
        options=display_entries,
        view_max=None
    )
    # Get the selected Path objects
    selected_paths = [path_map[display_entries[i]] for i in selection]

    # 3. Process selected items
    files = []
    full_files = []

    for item_path in selected_paths:
        if item_path.is_dir():
            # Use Path.glob for a simple recursive search (**/*)
            # or use Path.rglob() for cleaner code
            for file_path in item_path.rglob('*'):
                if file_path.suffix.lower() in ('.mp4', '.mkv'):
                    # The file name only
                    files.append(file_path.name)
                    # The full absolute path string
                    full_files.append(str(file_path.resolve()))
        elif item_path.suffix.lower() in ('.mp4', '.mkv'):
            # The file name only (it's already the file)
            files.append(item_path.name)
            # The full absolute path string
            full_files.append(str(item_path.resolve()))

    return files, full_files


def parse_episode_code(episode_code: str):
    """Return (season, episode) numbers from 'SxxExx', or (0, 0) if invalid."""
    match = re.search(r"[Ss](\d+)[Ee](\d+)", episode_code or "")
    if not match:
        return 0, 0
    return map(int, match.groups())


# == MAIN LOGIC ==
defaultjob['id'] = survey.routines.input('ID: ', value='tmdb-').strip()
ontmdb = defaultjob['id'].startswith('tmdb-')
mediatypes = ('tv', 'movie')
defaultjob['type'] = mediatypes[survey.routines.select(
    'Type: ', options=mediatypes)]

if ontmdb:
    tmdbid = defaultjob['id'][5:]
    sname, syear = get_media_info(tmdbid, defaultjob['type'])
else:
    sname, syear = '', 0

defaultjob['name'] = survey.routines.input('Name: ', value=sname)
defaultjob['year'] = survey.routines.numeric(
    'Year: ', value=int(syear), decimal=False)
print("WARNING: LOW QUALITY IS NOT CURRENTLY IMPLEMENTED!!!")
defaultjob['quality'] = qualities[survey.routines.select(
    'Quality: ', options=qualities)]

files = []
while not files:
    files, full_files = select_and_list_videos()
selection = ()
while not selection:
    selection = survey.routines.basket(
        'Select folders/files:', options=files, view_max=None, active=files)
full_files = [full_files[i] for i in selection]
filenames = [os.path.basename(files[i]) for i in selection]

# == TV SHOW ==
if defaultjob['type'] == 'tv':
    for findex in range(len(full_files)):
        output.append(deepcopy(defaultjob))
        output[-1]['input_file'] = full_files[findex]

        season, episode = parse_episode_code(filenames[findex])

        print(f'\n{filenames[findex]}')

        season = str(survey.routines.numeric('Season: ', value=season))
        episode = str(survey.routines.numeric('Episode: ', value=episode))
        if ontmdb:
            print('get from tmdb')
            episode_title = get_episode_title(tmdbid, season, episode)
        episode_title = survey.routines.input(
            'Episode Title: ', value=episode_title)

        # OUTPUT: pathtocd/Name (Year) {ID} OUTPUT/Season --/
        #         Name (Year) - s00e00 - EpName \[info\].ext
        seasonepisodestr = f's{int(season):02}e{int(episode):02}'
        output[-1]['encoded_file'] = OUTPUT_DIR / f'{
            output[-1]["name"]} ({output[-1]["year"]
                                  }) {{{output[-1]["id"]}}}' / \
            f'Season {int(season):02}' / \
            f'{output[-1]["name"]} ({output[-1]["year"]}) - {
                seasonepisodestr} - {episode_title}.mkv'
        output[-1]['encoded_file'] = str(output[-1]['encoded_file'])
        output[-1]['name'] = f'{output[-1]['name']} - {seasonepisodestr}'

# == MOVIE ==
else:
    if len(filenames) == 1:  # must be movie file
        output.append(deepcopy(defaultjob))
        output[-1]['input_file'] = full_files[0]
        output[-1]['encoded_file'] = OUTPUT_DIR / \
            f'{output[-1]["name"]} ({output[-1]["year"]}) {{{
                output[-1]["id"]}}}{
            output[-1]["name"]} ({output[-1]["year"]}) {{{
            output[-1]["id"]}}}.mkv'
        output[-1]['encoded_file'] = str(output[-1]['encoded_file'])
    else:
        full_files.sort(key=lambda f: os.path.getsize(f), reverse=True)

        # First (largest) file
        biggest = full_files[0]
        extras = full_files[1:]

        # Main file
        output.append(deepcopy(defaultjob))
        output[-1]['input_file'] = biggest
        middle_segment = f'{output[-1]["name"]} ({
            output[-1]["year"]}) {
            {{output[-1]["id"]}}}{
            output[-1]["name"]} ({output[-1]["year"]}) {
            {{output[-1]["id"]}}}.mkv'
        output[-1]['encoded_file'] = OUTPUT_DIR / middle_segment
        output[-1]['encoded_file'] = str(output[-1]['encoded_file'])

        # Extra files
        for f in extras:
            output.append(deepcopy(defaultjob))
            output[-1]['input_file'] = f

            middle_segment = f'{
                output[-1]["name"]} ({output[-1]["year"]}) {{{output[-1]["id"]}}}'
            final_file_name = Path(f).name
            output[-1]['encoded_file'] = OUTPUT_DIR / \
                middle_segment / 'extras' / final_file_name
            output[-1]['encoded_file'] = str(output[-1]['encoded_file'])

for thingy in output:
    thingy["before_size"] = os.path.getsize(thingy['input_file'])

with open(f'input-{str(int(time.time()))}.json', 'w') as f:
    f.write(json.dumps(output))
