import pytest
import pyfakefs
from types import GeneratorType
from rfirr import service

class TestPing:
    def test_ping_happy(self):
        host = '192.168.1.111'
        res = service.ping(host)
        assert isinstance(res, bool) 

    def test_not_string(self):
        host = None
        with pytest.raises(TypeError):
            service.ping(host)

class TestReadLogFile:
    log_good = '2021-04-28 18:01:34,904 INFO __main__ Plants watered for 5 seconds\nb2021-04-28 18:01:34,915 INFO __main__ rpi_zero turning off now\n2021-04-28 18:02:53,052 INFO rfirr.rf rpi_zero power is off'
    log_bad = '2021-04-28 18:01:34,904  __main__ Plants watered for 5 seconds\nb2021-04-28 18:01:34,915  __main__ rpi_zero turning off now\n2021-04-28 18:02:53,052  rfirr.rf rpi_zero power is off'

    def test_read_log_file_happy(self):
        log_file = pyfakefs.fake_filesystem.create_file('log.log', contents=self.log_good)
        gen = service.read_log_file(log_file)
        assert isinstance(gen, GeneratorType)

        

