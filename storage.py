# storage.py
import json

def load_tasks(filename: str = "tasks.json") -> list[dict]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_tasks(tasks: list[dict], filename: str = "tasks.json") -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)
