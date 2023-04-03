import csv
from datetime import datetime
from pathlib import Path

from rfirr.config import config

file_name = config['outside_rpi']['db']['file_path']
header = config['outside_rpi']['db']['columns']

def instantiate_db():
    Path(file_name).touch(exist_ok=True)
    with open(file_name, 'r') as fp:
        lines = fp.read().splitlines()
    if not lines:
        with open(file_name, 'w') as fp:
            fp.write(f"{header}\n")
        return
    if lines[0] != header:
        raise ValueError(f"CSV database header missing or malformed: {lines[0]}")

