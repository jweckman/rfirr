import os
import logging
import gpiozero
from time import sleep
from pathlib import Path
from datetime import datetime
import Adafruit_ADS1x15
from rfirr.config import config, device
from rfirr.service import capture_photo

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', level=logging.INFO, filename=Path(config[device]['log_path']) / 'log.log')
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
    print('ADC sensor values:')
    print(adc_sensor_values)

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
    adc_moisture_sensor_values, above_thresh_after = read_adc_moisture_sensor_values()
    if any(above_thresh_after.values()) and received_water:
        logger.critical(f"Water relay was triggered but moisture sensor was still below threshold")

    return received_water, above_thresh, above_thresh_after

def kill():
    '''Log that process has finished and shut down''' 
    shutdown_msg = f"{config['inside_rpi']['sensor']['rf']['controlled_device_name']} turning off now"
    logger.info(shutdown_msg)
    killcmd = 'sudo shutdown --poweroff'
    os.system(killcmd)

def outside_process():
    try:
        # capture photo
        path_photo = Path(config['outside_rpi']['sensor']['camera']['path']) / f"irr_img_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.jpg"
        capture_photo(path_photo)
        # water
        watering_process()
        # kill
        sleep(5)
        kill()
    except:
        sleep(10)
        kill()
