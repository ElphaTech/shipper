import survey
import os
import tmdbsimple as tmdb
import re
import dotenv
from copy import deepcopy
import time
import json

dotenv.load_dotenv()
tmdb.API_KEY = os.getenv('TMDB_API_KEY')

script_path = os.path.abspath(__file__)
script_directory = os.path.dirname(script_path)
with open(os.path.join(script_directory, "config.json")) as f:
    qualities = tuple(
        json.loads(f.read())['qualitypresets'].keys()
    )

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


def get_media_info(media_id: int, media_type: str):
    """
    Fetch general info about a TV show or movie.
    Returns a dict with:
      - title
      - year
    """
    try:
        if media_type == 'tv':
            tv = tmdb.TV(media_id)
            details = tv.info()
            return (
                details['name'],
                details['first_air_date'].split('-')[0]
            )
        elif media_type == 'movie':
            # Fallback to movie if TV lookup fails
            movie = tmdb.Movies(media_id)
            details = movie.info()
            return (
                details['title'],
                details['release_date'].split('-')[0]
            )
    except Exception:  # If anything goes wrong it is safe to return following
        return ('', 0)


def parse_episode_code(episode_code: str):
    """Return (season, episode) numbers from 'SxxExx', or (0, 0) if invalid."""
    match = re.search(r"[Ss](\d+)[Ee](\d+)", episode_code or "")
    if not match:
        return 0, 0
    return map(int, match.groups())


def get_episode_or_movie_info(media_id: int, episode_code: str = None):
    """
    Returns a list of strings:
    [season, episode, episode_title]
    If info can't be found, returns empty strings for missing values.
    """
    season = episode = episode_title = ""

    season_num, episode_num = parse_episode_code(episode_code)
    if not season_num or not episode_num:
        return [0, 0, ""]

    try:
        season_info = tmdb.TV_Seasons(media_id, season_num).info()
        episode_data = next(
            (ep for ep in season_info.get("episodes", [])
             if ep.get("episode_number") == episode_num),
            {}
        )
        season = season_num
        episode = episode_num
        episode_title = episode_data.get("name", "")
    except Exception:
        season = season_num
        episode = episode_num
        pass

    return [season, episode, episode_title]


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
        if ontmdb:
            season, episode, episode_title = get_episode_or_movie_info(
                tmdbid,
                filenames[findex]
            )
        else:
            season, episode = [
                parse_episode_code(filenames[findex])
            ]
            episode_title = ''

        print(f'\n{filenames[findex]}')
        season = str(survey.routines.numeric('Season: ', value=season))
        episode = str(survey.routines.numeric('Episode: ', value=episode))
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
