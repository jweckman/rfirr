import pytest
#import pyfakefs
from datetime import datetime
from pathlib import Path
from types import GeneratorType
from rfirr import service
from rfirr import config

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
    ''' pyfakefs does not seem to work at all with generators. Will have to create file on disk here'''

    # Add fs as second argument to use fake file system
    def test_read_log_file_happy(self, log_files):
        #log_file = fs.create_file('log.log', contents=self.log_good)
        log_file = 'log_good.log'
        gen = service.read_log_file(log_file)
        assert isinstance(gen, GeneratorType)

    def test_read_log_file_bad_date(self, log_files):
        #log_file = fs.create_file('log.log', contents=self.log_bad)
        log_file = 'log_bad.log'
        gen = service.read_log_file(log_file)
        with pytest.raises(ValueError):
            dates = [x[0] for x in gen]
            for d in dates:
                if d == '':
                    continue
                datetime.strptime(d.split(' ')[0], '%Y-%m-%d')

    def test_read_log_file_good_date(self, log_files):
        #log_file = fs.create_file('log.log', contents=self.log_bad)
        log_file = 'log_good.log'
        gen2 = service.read_log_file(log_file)
        dates = [x[0] for x in gen2]
        print(dates)
        for d in dates:
            if d == '':
                continue
            date = d.split(' ')[0].strip()
            print(date)
            dt = datetime.strptime(date, '%Y-%m-%d')
            assert isinstance(dt, datetime)

    def test_read_log_file_good_status(self, log_files):
        log_file = 'log_good.log'
        gen3 = service.read_log_file(log_file)
        statuses = [x[1] for x in gen3]
        for s in statuses:
            if s == '':
                continue
            assert s in ['INFO', 'CRITICAL', 'ERROR', 'DEBUG'] 

    def test_read_log_file_bad_status(self, log_files):
        log_file = 'log_bad.log'
        gen3 = service.read_log_file(log_file)
        statuses = [x[1] for x in gen3]
        for s in statuses:
            if s == '':
                continue
            assert s not in ['INFO', 'CRITICAL', 'ERROR', 'DEBUG'] 
