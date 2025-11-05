import survey
import os
import re
import tmdbsimple as tmdb
from copy import deepcopy
import time
import json
from functions.tmdb_client import get_media_info, get_episode_title
from functions.config import load_config

CONFIG = load_config()

tmdb.API_KEY = CONFIG.tmdb_api_key
tmdb.REQUESTS_TIMEOUT = 5

qualities = tuple(CONFIG.quality_presets.keys())
print(qualities, type(qualities))
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
    "job_end_time": 0
}


def select_and_list_videos():
    entries = sorted([
        e + '/' if os.path.isdir(e) else e
        for e in os.listdir('.')
        if not e.startswith('.') and (
            os.path.isdir(e) or e.endswith(('.mkv', '.mp4'))
        )
    ])

    selection = survey.routines.basket(
        'Select folders/files:', options=entries, view_max=None)
    selected = [entries[i] for i in selection]

    files = []
    full_files = []
    for item in selected:
        path = os.path.abspath(item.rstrip('/'))
        if os.path.isdir(path):
            for root, _, fs in os.walk(path):
                for f in fs:
                    if f.endswith(('.mp4', '.mkv')):
                        files.append(f)
                        full_files.append(os.path.join(root, f))
        elif path.endswith(('.mp4', '.mkv')):
            files.append(path)
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

        season, episode = [
            parse_episode_code(filenames[findex])
        ]
        print(f'\n{filenames[findex]}')

        season = str(survey.routines.numeric('Season: ', value=season))
        episode = str(survey.routines.numeric('Episode: ', value=episode))
        if ontmdb:
            episode_title = get_episode_title(tmdbid, season, episode)
        episode_title = survey.routines.input(
            'Episode Title: ', value=episode_title)

        # OUTPUT: pathtocd/Name (Year) {ID} OUTPUT/Season --/
        #         Name (Year) - s00e00 - EpName \[info\].ext
        seasonepisodestr = f's{int(season):02}e{int(episode):02}'
        output[-1]['encoded_file'] = os.path.join(
            os.path.abspath('.'),
            f'{output[-1]["name"]} ({output[-1]["year"]
                                     }) {{{output[-1]["id"]}}}',
            f'Season {int(season):02}',
            f'{output[-1]["name"]} ({output[-1]["year"]}) - {
                seasonepisodestr} - {episode_title}.mkv'
        )
        output[-1]['name'] = f'{output[-1]['name']} - {seasonepisodestr}'

# == MOVIE ==
else:
    if len(filenames) == 1:  # must be movie file
        output.append(deepcopy(defaultjob))
        output[-1]['input_file'] = full_files[0]
        output[-1]['encoded_file'] = os.path.join(
            os.path.abspath('.'),
            f'{output[-1]["name"]} ({output[-1]["year"]
                                     }) {{{output[-1]["id"]}}}',
            f'{output[-1]["name"]} ({output[-1]["year"]
                                     }) {{{output[-1]["id"]}}}.mkv',
        )
    else:
        full_files.sort(key=lambda f: os.path.getsize(f), reverse=True)

        # First (largest) file
        biggest = full_files[0]
        extras = full_files[1:]

        # Main file
        output.append(deepcopy(defaultjob))
        output[-1]['input_file'] = biggest
        output[-1]['encoded_file'] = os.path.join(
            os.path.abspath('.'),
            f'{output[-1]["name"]} ({output[-1]["year"]
                                     }) {{{output[-1]["id"]}}}',
            f'{output[-1]["name"]} ({output[-1]["year"]
                                     }) {{{output[-1]["id"]}}}.mkv',
        )

        # Extra files
        for f in extras:
            output.append(deepcopy(defaultjob))
            output[-1]['input_file'] = f
            output[-1]['encoded_file'] = os.path.join(
                os.path.abspath('.'),
                f'{output[-1]["name"]} ({output[-1]["year"]
                                         }) {{{output[-1]["id"]}}}',
                'extras',
                os.path.basename(f)
            )

for thingy in output:
    thingy["before_size"] = os.path.getsize(thingy['input_file'])

with open(f'input-{str(int(time.time()))}.json', 'w') as f:
    f.write(json.dumps(output))
