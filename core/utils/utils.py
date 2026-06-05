import json
from datetime import datetime
from pathlib import Path
from core.config import settings

CONTROL_FILE = Path(settings.CONTROL_FILE_PATH)
DATA_BASE_DIR = Path(settings.DATA_BASE_DIR)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def get_since() -> str:
    try:
        with CONTROL_FILE.open() as f:
            data = json.load(f)
            return data.get("since") or datetime.now().strftime(DATE_FORMAT)[:-3]
    except (FileNotFoundError, json.JSONDecodeError):
        return datetime.now().strftime(DATE_FORMAT)[:-3]


def save_since() -> None:
    CONTROL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CONTROL_FILE.open("w") as f:
        json.dump({"since": datetime.now().strftime(DATE_FORMAT)[:-3]}, f)


def format_timestamp(timestamp: str) -> str:
    dt = datetime.strptime(timestamp.rstrip("Z"), "%Y-%m-%d %H:%M:%S.%f")
    return dt.strftime("%Y-%m-%d %H_%M_%S")
