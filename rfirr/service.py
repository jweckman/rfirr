from collections import namedtuple
from file_read_backwards import FileReadBackwards
import os
import logging
from pathlib import Path
from rfirr.config import config,device

LogLine = namedtuple('LogLine', 'timestamp level name msg')

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', level=logging.INFO, filename=Path(config[device]['log_path']) / 'log.log')
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
    capture_photo_cmd = f"raspistill -o {str(path)}" 
    try:
        os.system(capture_photo_cmd)
        logger.info('Photo was taken')
    except Exception as e:
        logger.error('Failed to capture photo. Reason: {e}')


if __name__ == '__main__':
    pass
