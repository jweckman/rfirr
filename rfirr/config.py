import json
from pathlib import Path
from detect_device import detect_device

def init_config():
    global config
    global ROOT 
    ROOT = get_project_root()
    with open((ROOT / 'config.json'), 'r', encoding='utf-8') as fr:
        config = json.load(fr)
    return config

def init_device():
    global device
    device = detect_device()
    return device

def get_project_root() -> Path:
    return Path(__file__).parent.parent

config = init_config()
device = init_device()
