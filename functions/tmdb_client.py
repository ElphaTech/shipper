import tmdbsimple as tmdb


def get_media_info(media_id: int, media_type: str) -> tuple[str, int]:
    """
    Fetch general info (title and year) about a TV show or movie from TMDB.

    Returns:
        tuple[str, int]: A tuple containing (title: str, year: int).
                         Returns ('', 0) on any failure or if date data is missing.
    """
    try:
        if media_type == 'tv':
            tmdb_object = tmdb.TV(media_id)
            details = tmdb_object.info()
            date_key = 'first_air_date'

        elif media_type == 'movie':
            tmdb_object = tmdb.Movies(media_id)
            details = tmdb_object.info()
            date_key = 'release_date'

        else:
            return ('', 0)  # Handle unexpected media_type

        # Extract title
        title = details.get('name') or details.get('title', '')

        # Extract year
        date_str = details.get(date_key)
        year = 0
        if date_str and len(date_str) >= 4:
            try:
                # Only attempt to convert the first 4 characters to an integer
                year = int(date_str[:4])
            except ValueError:
                # If int conversion fails (e.g., date is "TBD"), year remains 0
                pass

        return (title, year)

    except Exception:
        return ('', 0)


def get_episode_title(media_id: int, season_num: int, episode_num: int) -> str:
    """
    Returns the episode title.
    If it cannot be found a blank string is returned.
    """

    if not media_id or not season_num or not episode_num:
        return ""

    try:
        season_info = tmdb.TV_Seasons(media_id, season_num).info()
        episode_title = next(
            (ep for ep in season_info.get("episodes", [])
             if ep.get("episode_number") == int(episode_num)),
            {}
        ).get("name", "")
    except Exception as e:
        print(e)
        episode_title = ""
        pass

    return episode_title


if __name__ == "__main__":
    from config import load_config

    CONFIG = load_config()
    tmdb.API_KEY = CONFIG.tmdb_api_key
    tmdb.REQUESTS_TIMEOUT = 5

    print("--- Running metadata.py tests ---")

    # Inception movie test
    title, year = get_media_info(media_id=27205, media_type='movie')
    print(f"Test Result (Inception): {title} ({year})")

    # No year tv test
    title, year = get_media_info(media_id=8234, media_type='tv')
    print(f"Test Result (7 La - Missing year): {title} ({year})")

    # Get title test...
    print(get_episode_title(209867, '1', '12'))
