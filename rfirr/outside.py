import os
import logging
import gpiozero
from time import sleep
from pathlib import Path
from datetime import datetime, time, timedelta
import Adafruit_ADS1x15
from jsonrpcserver import Success, method, serve, InvalidParams, Result, Error
from rfirr.config import config, device
from rfirr.service import capture_photo
from rfirr import db

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.INFO,
    filename=Path(config[device]['log_path']) / 'log.log'
)
logger = logging.getLogger(__name__)

def read_adc_moisture_sensor_values():  
    adc = Adafruit_ADS1x15.ADS1115()
    adc_sensors = config['outside_rpi']['sensor']['adc']['devices']
    adc_sensor_values = dict()
    above_thresh = dict()
    for id_str, sensor in adc_sensors.items():
        if 'moisture' not in sensor['name']:
            continue
        value = adc.read_adc(int(id_str), gain=config['outside_rpi']['sensor']['adc']['gain'])
        adc_sensor_values[int(id_str)] = value
        above_thresh[int(id_str)] = (sensor['thresh'] < value)

    return adc_sensor_values, above_thresh

def water_relay_toggle(water_relay):
    try:
        water_relay.on()
        sleep(config['outside_rpi']['sensor']['relay']['default_seconds_open'])
        water_relay.off()
        logger.info(f"Plants watered for {config['outside_rpi']['sensor']['relay']['default_seconds_open']} seconds")
    except:
        logger.error(f"Failed to water plants")
        water_relay.off()
    finally:
        water_relay.off()

def watering_process():
    adc_moisture_sensor_values, above_thresh = read_adc_moisture_sensor_values()
    if len(above_thresh) == 0:
        print("No adc devices containing the name 'moisture' - no moisture sensor input was read") 
    # let or do not let out water depending on moisture sensor output value 20_000'''
    water_relay = gpiozero.OutputDevice(config['outside_rpi']['sensor']['relay']['channel'])
    received_water = False
    for adc_channel, is_above_thresh in above_thresh.items():
        if is_above_thresh:
            logger.info(f"Trying to trigger water since adc channel {adc_channel} value was {adc_moisture_sensor_values[adc_channel]}")
            water_relay_toggle(water_relay)
            received_water = True
            break
    # Verify that plants got wet
    adc_moisture_sensor_values_after, above_thresh_after = read_adc_moisture_sensor_values()
    if any(above_thresh_after.values()) and received_water:
        logger.critical(f"Water relay was triggered but moisture sensor was still below threshold")

    return received_water, above_thresh, above_thresh_after, adc_moisture_sensor_values

def shut_down():
    '''Log that process has finished and shut down''' 
    shutdown_msg = f"{config['inside_rpi']['sensor']['rf']['controlled_device_name']} turning off now"
    logger.info(shutdown_msg)
    shutdown_cmd = 'sudo shutdown --poweroff'
    os.system(shutdown_cmd)

# RPC methods

@method
def get_status():
    read_res = db.read(start_date = datetime.now() - timedelta(days=10))
    read_res = read_res or ''
    return Success(read_res)

@method
def set_config_value(name, value) -> Result:
    v = None
    if name == 'duration':
        try:
            v = int(value)
        except:
            return InvalidParams('Value needs to be an integer')
        config['outside_rpi']['sensor']['relay']['default_seconds_open'] = v
        return Success(v)
    elif name == 'moisture':
        try:
            v = int(value)
        except:
            return InvalidParams('Value needs to be an integer')
        config['outside_rpi']['sensor']['adc']['devices']['0']['thresh'] = v
        return Success(v)
    elif name == 'auto':
        try:
            v = int(value)
        except:
            return InvalidParams('Value needs to be an integer')
        config['common']['auto_run']['enable'] = False if 0 else True
        return Success(v)
    elif name == 'time':
        try:

            hours, minutes = value.split(':')
            v = time(hour=hours, minute=minutes)
        except:
            return InvalidParams('Value needs to be a time string like 18:00')
        config['common']['auto_run']['time'] = v
        return Success(v)
    else:
        print('returned error')
        return Error(
            1,
            (
                "Fields duration or moisture should be set.\n"
                f"Currently: {config['outside_rpi']['sensor']['relay']['default_seconds_open']}, "
                f"{config['outside_rpi']['sensor']['adc']['devices']['0']['thresh']}, "
                f"{config['common']['auto_run']['enable']}, "
                f"{config['common']['auto_run']['time']}"
            )
        )

@method
def start_irrigation() -> Result:
    status = outside_process(do_shutdown=False)
    if status:
        return Success('Success')
    else:
        return Error(1, 'Error')

# RF mode main method

def outside_process(do_shutdown=False):
    '''Returns True if successful'''
    # TODO: implement dry_run and test on hardware
    status = False
    try:
        # capture photo
        path_photo = Path(config['outside_rpi']['sensor']['camera']['path']) / f"irr_img_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.jpg"
        capture_photo(path_photo)
        # water
        received_water, above_thresh, above_thresh_after, adc_moisture_sensor_values = watering_process()
        moisture_values = [mv for k, mv in adc_moisture_sensor_values.items() if mv > 0]
        if moisture_values:
            main_moisture = moisture_values[0]
        else:
            main_moisture = 0
        # kill
        status = True
        dl = {'date': datetime.now(), 'did_water': received_water, 'moisture': main_moisture}
        db.write_line(dl)
        if do_shutdown:
            sleep(5)
            kill()
    except:
        status = False
        if do_shutdown:
            sleep(10)
            kill()
    return status
