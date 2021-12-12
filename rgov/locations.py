import os
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent


PROJECT_ROOT = get_project_root()

DOWNLOAD_FOLDER = os.path.join(PROJECT_ROOT, "assets")
DOWNLOAD_PATH = os.path.join(DOWNLOAD_FOLDER, "RIDBExport.zip")
FACILITIES_CSV_PATH = os.path.join(DOWNLOAD_FOLDER, "Facilities_API_v1.csv")

DATA_FOLDER = os.path.join(PROJECT_ROOT, "data")
FACILITIES_DB = os.path.join(DATA_FOLDER, "rgov.db")

CONFIG_DIR = os.getenv("XDG_CONFIG_HOME", os.path.join(Path.home(), ".config"))
AUTH_FILE = os.path.join(CONFIG_DIR, "rgov", "auth.txt")
LOG_FILE = os.path.join(Path.home(), ".rgov.log")

EXAMPLE_DATA = os.path.join(DATA_FOLDER, "example.json")
