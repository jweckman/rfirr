import pytest
from datetime import datetime, timedelta

from rfirr.scheduling import schedule_daemon
from rfirr.config import config as global_config

@pytest.fixture()
def fixture_config_time_passed(monkeypatch):
    monkeypatch.setitem(
        global_config['common']['auto_run'],
        "time",
        (datetime.utcnow() - timedelta(seconds=30)).strftime('%H:%M')
    )
    monkeypatch.setitem(
        global_config['common']['auto_run'],
        "enable",
        True
    )
    monkeypatch.setitem(
        global_config['common']['auto_run'],
        "cycle_seconds",
        0.1
    )

@pytest.fixture()
def fixture_config_time_not_passed(monkeypatch):
    monkeypatch.setitem(
        global_config['common']['auto_run'],
        "time",
        (datetime.utcnow() + timedelta(seconds=300)).strftime('%H:%M')
    )
    monkeypatch.setitem(
        global_config['common']['auto_run'],
        "enable",
        True
    )
    monkeypatch.setitem(
        global_config['common']['auto_run'],
        "cycle_seconds",
        0.1
    )

@pytest.fixture()
def fixture_outside_process_returns_true(mocker):
    mocker.patch('rfirr.scheduling.outside_process', return_value=True)


class TestScheduling:
    def test_should_water(
            self,
            fixture_config_time_passed,
            fixture_outside_process_returns_true,
        ):
        res = schedule_daemon(cycles_max=6)
        assert res

    def test_should_not_water_ran_today_already(
            self,
            fixture_config_time_passed,
            fixture_outside_process_returns_true,
        ):
        res = schedule_daemon(cycles_max=6, ran_today=True)
        assert not res

    def test_should_not_water_time_not_passed(
            self,
            fixture_config_time_not_passed,
            fixture_outside_process_returns_true,
        ):
        res = schedule_daemon(cycles_max=6)
        assert not res
