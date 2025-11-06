import json


def read_file(filepath: str, default_data: str = "") -> str:
    '''
    A function to safely read files.
    If the file does not exist or is blank, it will return default_data.
    '''
    if filepath.exists():
        with open(filepath) as f:
            file_data = f.read()
            if file_data.strip():
                return file_data

    return default_data


def write_file(filepath: str, data: str = None):
    '''
    A function to write to a file.
    If no data is given, the file will not be changed.
    '''
    if data:
        with open(filepath, 'w') as f:
            f.write(data)


def load_json(filepath: str) -> dict:
    '''
    Returns a json file as a dictionary.
    If the file is missing/blank then it returns an empty dictionary.
    '''
    return json.loads(read_file(
        filepath,
        '{}'
    ))


def save_json(filepath: str, data: dict):
    '''
    Saves the json data to the filepath.
    '''
    write_file(
        filepath,
        json.dumps(data)
    )
