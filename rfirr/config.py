import json
import os
from pathlib import Path

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

def detect_device():
    ''' Tries to detect which device is running the code. If successful, there is no need to manually set which is the inside and outside deivce.
    NB! Only made with Raspberry Pi models in mind. Any other system will probably have to either modify this code or split the code manually'''

    error_msg = 'Unable to detect rpi type from /sys/firmware/devicetree/base/model. Consider splitting the code manually in the main module'
    try:
        model = os.popen('cat /sys/firmware/devicetree/base/model').read()
    except Exception as e:
        raise e
    inside_models = config['inside_rpi']['model_names']
    outside_models = config['outside_rpi']['model_names']
    
    if any([x for x in inside_models if x in model]):
        return 'inside_rpi'
    elif any([x for x in outside_models if x in model]):
        return 'outside_rpi'
    else:
        raise RuntimeError(error_msg) 

config = init_config()
device = init_device()
