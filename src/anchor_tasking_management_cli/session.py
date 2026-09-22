import json
from pathlib import Path

FILE_PATH = Path.home() / ".config" / "usr_data.json"

def save_session(data:dict):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f)

def restore_session():
    if FILE_PATH.exists():
        FILE_PATH.unlink()

def load_session():
    try:
        with open(FILE_PATH, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else None
    except:
        return None