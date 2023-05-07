from datetime import datetime, timedelta
import time

from rfirr.config import config
from rfirr.service import str_to_time
from rfirr.outside import outside_process

def schedule_daemon(
        cycles_max = 999999999999999999999,
        ran_today = False,
        cycles_without_action = 0,
        last_ran = None,
    ):
    '''
    Since the Http server run by jsonrpcserver takes over the program
    we need to run the automated scheduling as a daemon using threading.

    The schedule library has very nice API but cannot be used.
    '''
    i = 0
    while True:
        now = datetime.utcnow()
        config_time = str_to_time(config.auto_run_time)
        autorun_enabled = config.auto_run_enabled
        next_run_dt = datetime(
            year = now.year,
            month = now.month,
            day = now.day,
            hour = config_time.tm_hour,
            minute = config_time.tm_min,
        )
        if last_ran:
            if last_ran.day != now.day:
                ran_today = False
        if config.test_mode:
            print(f"now: {now}")
            print(f"no action: {cycles_without_action}\nnext_run: {next_run_dt}\nRan today: {ran_today}")
        if (now > next_run_dt
                and ran_today == False
                and cycles_without_action > 4
            ):
            did_water = outside_process()
            ran_today = True
            cycles_without_action = 0
            last_ran = now
        else:
            cycles_without_action += 1

        time.sleep(config.auto_run_cycle_seconds)
        if i == cycles_max:
            return last_ran
        i += 1
