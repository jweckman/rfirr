import pytest

@pytest.fixture(scope="session", autouse=True)
def fixture_set_default_device(session_mocker):
    '''This is not actually required but more added a documentation
    for writing tricky tests. Also serves to show that the
    config.device is currently hard coded in all tests'''
    session_mocker.patch("rfirr.config.device", "outside_rpi")

@pytest.fixture(scope="session", autouse=True)
def fixture_moisture_sensor_values(session_mocker):
    '''Mock the adc moisture sensor values to something close to real world
    in all tests'''
    sensor_values = (
            [18000,0,0,0],
            {0: True, 1: False, 2: False, 3: False},
    )
    def return_sensor_values():
        return sensor_values
    session_mocker.patch(
        "rfirr.outside.read_adc_moisture_sensor_values",
        return_sensor_values
    )
