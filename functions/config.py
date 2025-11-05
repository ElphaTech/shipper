import os
import json
import dotenv  # <-- ADDED
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE_PATH = PROJECT_ROOT / "config.json"
DOTENV_PATH = PROJECT_ROOT / ".env"

# local config files just for me
LOCAL_CONFIG_FILE_PATH = PROJECT_ROOT / "config.local.json"
LOCAL_DOTENV_PATH = PROJECT_ROOT / ".local.env"
if LOCAL_CONFIG_FILE_PATH.exists():
    CONFIG_FILE_PATH = LOCAL_CONFIG_FILE_PATH
print(CONFIG_FILE_PATH, LOCAL_CONFIG_FILE_PATH)
if LOCAL_DOTENV_PATH.exists():
    DOTENV_PATH = LOCAL_DOTENV_PATH


class Config:
    """
    Holds all application-wide configuration settings.
    """

    def __init__(self, raw_config: Dict[str, Any]):
        """Initializes the Config object from a dictionary of settings."""

        # --- 1. TMDB API Key (From Environment) ---
        # os.getenv works because dotenv.load_dotenv() ran below
        self.tmdb_api_key: str = os.getenv('TMDB_API_KEY', '').strip()
        if not self.tmdb_api_key:
            # Using print() here is acceptable for a critical startup error
            print("Error: TMDB_API_KEY environment variable is not set.")

        # --- 2. Job Limits (From config.json) ---
        job_limits = raw_config.get('job_limits', {})
        self.max_encode_jobs: int = job_limits.get('encode', 1)
        self.max_frame_count_jobs: int = job_limits.get('frame_count', 1)

        # --- 3. Quality Presets (From config.json) ---
        self.quality_presets: Dict[str, str] = raw_config.get(
            'quality_presets', {})

        # --- 4. Paths (Added default paths if you introduce them) ---
        self.input_dir: Path = Path(raw_config.get('input_path', '.'))
        self.output_dir: Path = Path(
            raw_config.get('output_path', './Encoded'))


def load_config() -> Config:
    """
    Loads environment variables and config.json, then returns a Config object.
    """

    try:
        dotenv.load_dotenv(DOTENV_PATH)
    except Exception as e:
        # Handle cases where the .env file might not exist or be readable
        print(f"Warning: Could not load .env file from {
              DOTENV_PATH}. Error: {e}")

    raw_config_data = {}

    if CONFIG_FILE_PATH.exists():
        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                raw_config_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Could not parse {
                  CONFIG_FILE_PATH}. Check JSON syntax.")
        except Exception as e:
            print(f"Error reading config file: {e}")

    # Create and return the final, structured Config object
    return Config(raw_config_data)


if __name__ == "__main__":
    app_config = load_config()
    print(f"Max Encoding Jobs: {app_config.max_encode_jobs}")
    print(f"TMDB Key Loaded: {bool(app_config.tmdb_api_key)}")
