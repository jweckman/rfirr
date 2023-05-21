from collections import namedtuple
from file_read_backwards import FileReadBackwards
import os
import logging
from pathlib import Path
from datetime import datetime
import time
from rfirr.config import config

LogLine = namedtuple('LogLine', 'timestamp level name msg')

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.INFO,
    filename=Path(config.get('log_path')) / 'log.log')
logger = logging.getLogger(__name__)

def read_log_file(f):
    ''' Returns a generator that gives log file rows backwards as named tuples.
        NB! Logs have to follow a specific pattern for this to work'''
    frb = None
    try:
        frb = FileReadBackwards(f, encoding='utf-8')
        while True:
            l = frb.readline()
            if not l:
                break
            l = l.replace('\n', '')
            try:
                if len(l) > 30:
                    parts = l.split(' ')
                    yield LogLine(timestamp=' '.join(parts[0:2]), level=parts[2], name=parts[3], msg=' '.join(parts[4:]))
            except GeneratorExit: 
                pass
            else:
                yield LogLine('','','','') 
        frb.close()
    except GeneratorExit:
        pass
    else:
        if frb:
            frb.close()

def ping(hostname:str):
    ''' Finds out whether a host is up or not'''
    response = os.system("ping -c 1 -w2 " + hostname + " > /dev/null 2>&1")
    if response == 0:
        return True 
    else:
        return False 

def capture_photo(path):
    if config.test_mode:
        print('TEST: Photo taking simulated')
        return
    capture_photo_cmd = f"raspistill -o {str(path)}" 
    try:
        os.system(capture_photo_cmd)
        logger.info('Photo was taken')
    except Exception as e:
        logger.warning('Failed to capture photo. Reason: {e}')

def str_to_date(s:str):
    if 'T' in s:
        res = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
    else:
        res = datetime.strptime(s, "%Y-%m-%d")
    return res

def date_to_str(d:datetime):
    return datetime.strftime(d, "%Y-%m-%dT%H:%M:%S")

def str_to_time(s:str):
    res = None
    try:
        hours, minutes = s.split(':')
        res = time.strptime(s, '%H:%M')
    except:
        raise Warning(f"Time {s} could not be converted to a time object")
    return res

if __name__ == '__main__':
    pass
