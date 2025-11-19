# Data Properties
This is a list of all properties in the data file.

# Exemplar Data
This is exemplar data from a file that has completed encoding.
```json
{
  "1": {
    "id": "test",
    "name": "series-name - s01e01",
    "year": 1994,
    "quality": "very_low",
    "type": "tv",
    "status": "encoded",
    "input_file": "/home/user/input/series-name/episode-name-that-is-long.mp4",
    "encoded_file": "/home/user/output/series-name (1994) {id}/Season 01/series-name (1994) - s01e01 - episode-name.mkv",
    "before_size": 208322610,
    "after_size": 0,
    "percentage_encoded": 0,
    "percentage_copied": 0,
    "job_start_time": 1763504031,
    "encode_start_time": 1763504031,
    "encode_end_time": 0,
    "copy_start_time": 0,
    "copy_end_time": 0,
    "job_end_time": 0,
    "current_frames": 0,
    "frames": 32849,
    "current_frame": 32849
  }
}
```

**uid**
The key for the job. It is generated upon importing the job to the daemon by getting the biggest UID in the data file and adding 1 to it.

**id**
The id of the media, usually tmdb-0000 where 0000 is the id of the show. Used by input script to get show info and naming output files for Plex.

**name**
TV Shows: Season name combined with season and episode numbers.
Movies: Name of the movie.

**year**
The year that the show was released.

**quality**
The quality preset name found in the config.json file. Used when encoding the output.

**type**
The type of media. Currently, only `tv` (show) and `movie` are supported.

**status**
Can be one of the following:
- `not_started`
- `getting_frames`
- `ready_to_encode`
- `encoding`
- `error`
- `encoded`

**input_file**
The full path of the input file.

**output_file**
The full path of the output file.

**before_size**
The size of the input file in bytes.

**after_size** (unused)
The size of the output file in bytes.

**percentage_encoded** (unused)
A decimal value that is the current number of encoded frames divided by the total number of frames in the input file.

**percentage_copied** (unused)
To be removed.

**job_start_time**
A unix timestamp representing the time at which the file started being encoded.

**encode_start_time**
A unix timestamp representing the time at which the file started being encoded.

**encode_end_time**
A unix timestamp representing the time at which the file finished being encoded.

**copy_start_time**
To be removed.

**copy_end_time**
To be removed.

**job_end_time**
A unix timestamp representing the time at which the file finished being encoded.

**current_frames**
To be removed?

**frames**
The number of frames in the original video.

**current_frame**
The frame that is currently being encoded.
