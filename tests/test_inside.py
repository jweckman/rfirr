import pytest
from rfirr import rf
from rfirr.inside import retries
from rfirr.config import config as global_config
from rfirr import service

@pytest.fixture()
def log_files():
    print('setup')
    log_good = '2021-04-28 18:01:34,904 INFO __main__ Plants watered for 5 seconds\n2021-04-28 18:01:34,915 INFO __main__ rpi_zero turning off now\n2021-04-28 18:02:53,052 INFO rfirr.rf rpi_zero power is off'
    log_bad = '2021-04-28 18:01:34,904  __main__ Plants watered for 5 seconds\nb2021-04-28 18:01:34,915  __main__ rpi_zero turning off now\n2021-04-28 18:02:53,052  rfirr.rf rpi_zero power is off'
    with open('log_good.log', 'w') as fw:
        fw.write(log_good)
    with open('log_bad.log', 'w') as fw:
        fw.write(log_bad)
    with open('log_good.log', 'r') as fr:
        data = fr.read()
        print(data)
    yield "log_files"
    print('teardown')
    Path('log_good.log').unlink()
    Path('log_bad.log').unlink()

class MockedPowerSwitch:
    def __init__(self):
        self.is_on = False
    def toggle(self):
        if self.is_on:
            self.is_on = False
        else:
            self.is_on = True
    def cleanup(self):
        pass

@pytest.fixture()
def fixture_power_switch(mocker):
    mocker.patch.object(
            rf,
            "RadioOutputDevice",
            MockedPowerSwitch
    )

@pytest.fixture()
def fixture_ping_returns_false(mocker):
    mocker.patch('rfirr.inside.ping', return_value=False)

@pytest.fixture()
def fixture_ping_returns_true(mocker):
    mocker.patch('rfirr.inside.ping', return_value=True)

@pytest.fixture()
def fixture_lower_delays(monkeypatch):
    monkeypatch.setitem(
            global_config['inside_rpi']['delays'],
            "after_wakeup",
            0.01
    )
    monkeypatch.setitem(
            global_config['inside_rpi']['delays'],
            "wake_up_retry",
            0.01
    )

class TestRetries:
    def test_should_fail_if_off(self,
            fixture_power_switch,
            fixture_lower_delays,
            fixture_ping_returns_false
        ):
        with pytest.raises(RuntimeError): 
            rpi_is_on, power_switch = retries('inside_rpi', MockedPowerSwitch())

    def test_should_be_on_if_pingable(
            self,
            mocker,
            fixture_power_switch,
            fixture_lower_delays,
            fixture_ping_returns_true
        ):
        rpi_is_on, power_switch = retries('inside_rpi', MockedPowerSwitch())
        assert rpi_is_on
        assert power_switch.is_on

