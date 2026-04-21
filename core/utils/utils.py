import json
from datetime import datetime
import os
import dotenv

dotenv.load_dotenv()

CONTROL_FILE = os.getenv("CONTROL_FILE_PATH")
DATA_BASE_DIR = os.getenv("DATA_BASE_DIR")
DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def get_since() -> str:
    try:
        with open(CONTROL_FILE) as f:
            data = json.load(f)
            return data.get("since") or datetime.now().strftime(DATE_FORMAT)[:-3]
    except (FileNotFoundError, json.JSONDecodeError):
        return datetime.now().strftime(DATE_FORMAT)[:-3]


def save_since() -> None:
    with open(CONTROL_FILE, "w") as f:
        json.dump({"since": datetime.now().strftime(DATE_FORMAT)[:-3]}, f)
