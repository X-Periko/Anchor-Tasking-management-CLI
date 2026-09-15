import json
from pathlib import Path

FILE_PATH = Path.home() / ".config" / "usr_data.json"

def save_session(data:dict):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f)

def restore_session():
    with open(FILE_PATH, "w") as f:
        json.dump("", f)

def load_session():
    with open(FILE_PATH, "r") as f:
        return json.load(f)