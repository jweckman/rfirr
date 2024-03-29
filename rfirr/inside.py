import logging
from time import sleep
from pathlib import Path
from rfirr.rf import RadioOutputDevice
from rfirr.config import config
from rfirr.service import ping, read_log_file

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', level=logging.INFO, filename=Path(config.get('log_path')) / 'log.log')
logger = logging.getLogger(__name__)

def initial_start(power_switch):
    ''' Reads status and toggles power if needed'''
    rpi_zero_status = power_switch.get_value()
    print(f"rpi_zero status is: {rpi_zero_status}")
    if power_switch.value == 0:
        print('Outside power was toggled by inside')
        power_switch.toggle()
    sleep(config.inside_delays['after_wake_up'])

def retries(name, power_switch):
    ''' Retries to toggle power if first time was unsuccessful'''
    is_on = False
    for i in range(4):
        is_on = ping(config.outside_ip)
        if is_on:
            power_switch.is_on = True
            break
        else:
            print('Outside power was toggled by inside')
            logger.info(f"Outside did not turn on after first try. Retrying {i}..")
            power_switch.toggle()
            sleep(config.inside_delays['wake_up_retry'])
    if not is_on:
        error_msg = f"{name} never started"
        logger.warning(error_msg)
        raise RuntimeError(error_msg)
    return is_on, power_switch

def kill(name, power_switch):
    ''' Kills out power after it has become unresponsive or signalled that it initiated shutdown '''
    outside_ping = ping(config.outside_ip)
    while outside_ping:
        outside_ping = ping(config.outside_ip)
        log_reader = read_log_file(Path(config.get('log_path')) / 'log.log')
        for log_tuple in log_reader:
            if f"{name} power is on" in log_tuple.msg:
                sleep(config.inside_delays['power_still_on'])
                break
            if f"{name} turning off now" in log_tuple.msg:
                sleep(config.inside_delays['powering_off'])
                outside_ping = False
                break
    print('Outside power was toggled by inside')
    power_switch.toggle()
    power_switch.cleanup()

def inside_process():
    controlled_device_name = config.inside_sensors['rf']['controlled_device_name']
    rpi_zero_power = RadioOutputDevice( config.inside_sensors['rf']['channel'],
                                        config.inside_sensors['rf']['code'],
                                        controlled_device_name,
                                        log_file=Path(config.get('log_path')) / 'log.log'
    )
    initial_start(rpi_zero_power)
    retries(controlled_device_name, rpi_zero_power)
    kill(controlled_device_name, rpi_zero_power)
