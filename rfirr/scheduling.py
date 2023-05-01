from datetime import datetime
import time
from rfirr.config import config

def schedule_daemon():
    '''
    Since the Http server run by jsonrpcserver takes over the program
    we need to run the automated scheduling as a daemon using threading.

    The schedule library has  very nice API but cannot be used.
    '''
    while True:
        # TODO: write custom logic for reading config time
        # and running when it hits the next time
        time.sleep(1)
