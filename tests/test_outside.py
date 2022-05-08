import pytest
from rfirr.outside import watering_process
from rfirr.config import config as global_config
import gpiozero


class MockedWaterRelay:
    def __init__(self, channel):
        self.is_on = False
        self.channel = channel
    def on(self):
        self.is_on = True
    def off(self):
        self.is_on = False

@pytest.fixture()
def fixture_gpiozero_water_relay(mocker):
    mocker.patch.object(
            gpiozero,
            "OutputDevice",
            MockedWaterRelay
    )

@pytest.fixture()
def fixture_set_water_relay_sleep(monkeypatch):
    monkeypatch.setitem(
            global_config['outside_rpi']['sensor']['relay'],
            "default_seconds_open",
            0.1
    )

class TestSensorRelated:
    '''Watering process sensor values are mocked globally in conftest.py'''

    def test_watering_process_received_water(self,
            fixture_gpiozero_water_relay,
            fixture_set_water_relay_sleep):
        received_water, above_thresh, above_thresh_after = watering_process()
        assert received_water == True
        assert True in above_thresh

    def test_watering_process_verification(self,
            fixture_gpiozero_water_relay,
            fixture_set_water_relay_sleep):
        received_water, above_thresh, above_thresh_after = watering_process()
        assert True in above_thresh_after

