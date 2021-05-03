import json
from pathlib import Path
import os
import logging
from time import sleep
from datetime import datetime
import Adafruit_ADS1x15
import gpiozero
from rfirr.rf import RadioOutputDevice
from rfirr.service import ping, read_log_file
from detect_device import detect_device

# Setup
device = detect_device()
with open('config.json', 'r', encoding='utf-8') as fr:
    config = json.load(fr)

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', level=logging.INFO, filename=Path(config[device]['log_path']) / 'log.log')
logger = logging.getLogger(__name__)


# Step 1: In gets weather data and stores it somewhere
# TODO

# Step 2: In wakes up out
def inside():
    rpi_zero_power = RadioOutputDevice(23, 654321, config['inside_rpi']['sensor']['rf']['controlled_device_name'], log_file=Path(config['inside_rpi']['log_path']) / 'log.log')
    print(rpi_zero_power.get_value())
    if rpi_zero_power.value == 0:
        print('Outside power was toggled by inside')
        rpi_zero_power.toggle()
    sleep(75)
    is_on = False
    for i in range(4):
        is_on = ping(config['outside_rpi']['ip_address'])
        if is_on:
            break
        else:
            print('Outside power was toggled by inside')
            logger.info(f"Outside did not turn on after first try. Retrying {i}..")
            rpi_zero_power.toggle()
            sleep(75)
    if not is_on:
        error_msg = f"{config['inside_rpi']['sensor']['rf']['controlled_device_name']} never started"
        logger.exception(error_msg)
        raise RuntimeError(error_msg)

    # Step 9: In kills out power after it has become responsive or signalled that it initiated shutdown in one minute  
    while ping(config['outside_rpi']['ip_address']):
        log_reader = read_log_file(Path(config['inside_rpi']['log_path']) / 'log.log')
        for log_tuple in log_reader:
            if f"{config['inside_rpi']['sensor']['rf']['controlled_device_name']} power is on" in log_tuple.msg:
                sleep(30)
            if f"{config['inside_rpi']['sensor']['rf']['controlled_device_name']} turning off now" in log_tuple.msg:
                sleep(80)
                break
    print('Outside power was toggled by inside')
    rpi_zero_power.toggle()
    rpi_zero_power.cleanup()


def outside():
    # Step 3: Out checks moisture
    adc = Adafruit_ADS1x15.ADS1115()
    adc_sensors = config['outside_rpi']['sensor']['adc']['devices']
    adc_sensor_values = dict()  
    for id_str, sensor in adc_sensors.items():
        adc_sensor_values[int(id_str)] = adc.read_adc(int(id_str), gain=config['outside_rpi']['sensor']['adc']['gain'])
    print(adc_sensor_values)


    # Step 4: Camera takes picture
    path_photo = Path(config['outside_rpi']['sensor']['camera']['path']) / f"irr_img_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.jpg"
    print(path_photo)
    capture_photo_cmd = f"raspistill -o {str(path_photo)}" 
    os.system(capture_photo_cmd)

    # Step 5: Out lets or does not let out water 
    if any([sv > 20_000 for sv in adc_sensor_values.values()]):
        water_relay = gpiozero.OutputDevice(config['outside_rpi']['sensor']['relay']['channel'])
        print(water_relay.value)
        try:
            water_relay.on()
            print(water_relay.value)
            sleep(config['outside_rpi']['sensor']['relay']['default_seconds_open'])
            water_relay.off()
            logger.info(f"Plants watered for {config['outside_rpi']['sensor']['relay']['default_seconds_open']} seconds")
        except:
            logger.error(f"Failed to water plants")
            water_relay.off()
        finally:
            water_relay.off()

    # Step 6: Out checks moisture

    # Step 7: Camera takes picture 

    # Step 8: Out logs that it finished and turns itself off
    shutdown_msg = f"{config['inside_rpi']['sensor']['rf']['controlled_device_name']} turning off now"
    logger.info(shutdown_msg)
    killcmd = 'sudo shutdown --poweroff'
    os.system(killcmd)

if device == 'inside_rpi':
    inside()
elif device == 'outside_rpi':
    outside()
