import json
import os
from enum import Enum, auto
from pathlib import Path
from typing import Any

def init_config():
    return Config()

class DeviceType(Enum):
    OUTSIDE_RPI = auto()
    INSIDE_RPI = auto()

device_to_conf_name = {
    DeviceType.OUTSIDE_RPI: 'outside_',
    DeviceType.INSIDE_RPI: 'inside_',
}

class Config:
    def __init__(self, config_path=None):
        self.project_root = self._get_project_root()
        if not config_path:
            self.json = self._read_json(self.project_root / 'config.json')
        else:
            self.json = self._read_json(Path(config_path))

        self.test_mode = self.json['common']['test_mode']
        self.mode = self.json['common']['mode']
        self.auto_run_enabled = bool(self.json['common']['auto_run']['enable'])
        self.auto_run_time = self.json['common']['auto_run']['time']
        self.auto_run_cycle_seconds = self.json['common']['auto_run']['cycle_seconds']
        self.device = self.detect_device()

        self.inside_model_names = self.json['inside_rpi']['model_names']
        self.inside_ip = self.json['inside_rpi']['ip_address']
        self.inside_log_path = self.json['inside_rpi']['log_path']
        self.inside_sensors = self.json['inside_rpi']['sensor']
        self.inside_delays = self.json['inside_rpi']['delays']

        self.outside_model_names = self.json['outside_rpi']['model_names']
        self.outside_ip = self.json['outside_rpi']['ip_address']
        self.outside_log_path = self.json['outside_rpi']['log_path']
        self.outside_db = self.json['outside_rpi']['db']
        self.outside_sensors = self.json['outside_rpi']['sensor']

    def get(self, param: str) -> Any:
        '''
        There are a number of configs that are the same for all
        devices. Using get to fetch a config by name will get
        the config for the current device.
        '''
        conf_name = device_to_conf_name[self.device] + param
        return getattr(self, conf_name)

    def _read_json(self, path: Path) -> dict:
        with open(path, 'r', encoding='utf-8') as fr:
            config = json.load(fr)
        return config

    def _get_project_root(self) -> Path:
        return Path(__file__).parent.parent

    def detect_device(self) -> DeviceType:
        ''' Tries to detect which device is running the code. If successful, there is no need to manually set which is the inside and outside deivce.
        NB! Only made with Raspberry Pi models in mind. Any other system will probably have to either modify this code or split the code manually'''
        import sys

        if "pytest" in sys.modules or self.test_mode:
            print('Test mode detected, setting device to outside_rpi to start out')
            return DeviceType.OUTSIDE_RPI

        error_msg = 'Unable to detect rpi type from /sys/firmware/devicetree/base/model. Consider splitting the code manually in the main module'
        try:
            model = os.popen('cat /sys/firmware/devicetree/base/model').read()
        except Exception as e:
            raise e
        inside_models = config.inside_model_names
        outside_models = config.outside_model_names

        if any([x for x in inside_models if x in model]):
            return DeviceType.INSIDE_RPI
        elif any([x for x in outside_models if x in model]):
            return DeviceType.OUTSIDE_RPI
        else:
            raise RuntimeError(error_msg) 

config = init_config()
