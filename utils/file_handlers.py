from pathlib import Path
import json, os

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def save_json(obj, path):
    p = Path(path)
    ensure_dir(p.parent)
    p.write_text(json.dumps(obj, indent=2), encoding='utf-8')
    return str(p)

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))
