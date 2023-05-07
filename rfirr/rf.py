import logging
import json
from pathlib import Path
import sys
with open('config.json', 'r', encoding='utf-8') as fr:
    raw_config = json.load(fr)

if "pytest" in sys.modules or raw_config['common']['test_mode'] == True:
    # from tests.test_inside import RFDevice
    class RFDevice:
        pass
else:
    from rpi_rf import RFDevice
from rfirr.service import read_log_file, ping
from rfirr.config import config


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', level=logging.INFO, filename=Path(config.inside_log_path) / 'log.log')
logger = logging.getLogger(__name__)

class RadioOutputDevice(RFDevice):
    ''' Merges the ideas from gpiozero.OutputDevice and rpi_rf.RFDevice for unified API.
        Since this piece of code is arguably the most critical in the whole application,
        special care is taken to ensure that the class uses all the information available
        to guess whether the RF device activated by a rf code is in an "on" or "off" state.

        This class could be used to directly control water flow, but it is recommended
        to control only the outside control unit (e.g. raspberry pi zero), which can
        then communicate back through logging whether it is turned on, or ready to 
        be shut down after it has completed the tasks at hand.
        '''

    def __init__(self, gpio: int, code: int, name: str, tx_protocol=None, tx_pulse_length=None, log_file='log.log'):
        super().__init__(self)
        self.gpio = gpio 
        self.code = code
        # Always initialized with unknown state (0 = off, 1 = on. "value" name used from gpiozero library for consistency  
        self.value = None
        self.name = name
        self.tx_protocol = tx_protocol
        self.tx_pulse_length = tx_pulse_length
        self.enable_tx()
        self.log_file = log_file

    def toggle(self):
        ''' Sends the radio signal code which toggles the device to be on or off'''
        self.tx_code(code=self.code)
        if self.value is None:
            logger.warning('Radio device toggled without knowing whether it was on or off')
        elif self.value == 0:
            logger.info(f"{self.name} power is on")
            self.value = 1
        elif self.value == 1:
            logger.info(f"{self.name} power is off")
            self.value = 0

    def get_value(self):
        ''' Sets the state to 0 (off) or 1 (on) depending on external information.
            The standard implementation is a shared log file and ping, but e.g. voltage
            meter or some other sensor could also be used to know whether
            the device is on or not. Ideally we would use a pulse mode to keep
            the device on as long as there is a signal, but i could not make
            that work with my hardware and therefore had to resort to other means
            of finding out whether the controlled device is on or not'''
        if ping(config.outside_ip):
            self.value = 1
            return 1
        log_file_generator = read_log_file(self.log_file)
        for log_line in log_file_generator:
            # Working with a generator here that returns named tuples
            # starting from the end of the file
            if log_line.msg == f"{self.name} power is on":
                self.value = 1
                return 1
            if log_line.msg == f"{self.name} power is off":
                self.value = 0
                return 0
        logger.exception(f"Could not find radio device {self.name} state. Aborting")
        raise ValueError(f"Could not find radio device {self.name} state. Aborting")

