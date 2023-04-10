import pytest
from pathlib import Path
from datetime import datetime

from rfirr.config import config as global_config
from rfirr import db

@pytest.fixture()
def db_csv_files():
    print('setup')
    header = 'date,did_water,moisture'
    record_ok = '2023-04-04T12:00:00,0,12000\n'
    record_bad_type = '2023-04-04T12:00:00,a_string,12000'
    db_ok = f"{header}\n{record_ok}"
    db_missing_header = record_ok
    db_bad_data = f"{header}\n{record_bad_type}"
    with open('db_ok.csv', 'w') as fw:
        fw.write(db_ok)
    with open('db_missing_header.csv', 'w') as fw:
        fw.write(db_missing_header)
    with open('db_bad_data.csv', 'w') as fw:
        fw.write(db_bad_data)
    yield "db_csv_files"
    print('teardown')
    Path('db_ok.csv').unlink()
    Path('db_missing_header.csv').unlink()
    Path('db_bad_data.csv').unlink()

class TestInstantiation:
    def test_should_not_fail_on_valid_data(
            self,
            db_csv_files,
        ):
        '''Validate existence of csv columns before doing anything'''
        file_name = "db_ok.csv"
        db.file_name = file_name
        db.instantiate_db()
        with open(file_name) as fp:
            data = fp.read()
        header = 'date,did_water,moisture'
        record_ok = '2023-04-04T12:00:00,0,12000'
        db_ok = f"{header}\n{record_ok}\n"
        assert data == db_ok

    def test_should_write_header_when_file_empty(
            self,
            db_csv_files,
        ):
        '''Validate existence of csv columns before doing anything'''
        file_name = "db_empty.csv"
        db.file_name = file_name
        db.instantiate_db()
        with open(file_name) as fp:
            data = fp.read()
        Path(file_name).unlink()
        header = 'date,did_water,moisture'
        db_ok = f"{header}\n"
        assert data == db_ok

    def test_should_fail_on_malformed_header(
            self,
            db_csv_files,
            ):
        file_name = "db_missing_header.csv"
        db.file_name = file_name
        with pytest.raises(ValueError):
            db.instantiate_db()

class TestRead:
    def test_should_read_ok_file(
            self,
            db_csv_files,
        ):
        file_name = "db_ok.csv"
        db.file_name = file_name
        # db.instantiate_db()
        record_ok = '2023-04-04T12:00:00,0,12000'
        res = db.read("2023-04-03")
        expected_date = datetime.strptime('2023-04-04T12:00:00', '%Y-%m-%dT%H:%M:%S')
        assert res == [
            {'date': expected_date, 'did_water': False, 'moisture': 12000},
        ]

class TestWrite:
    def test_write_to_ok_file(
            self,
            db_csv_files,
        ):
        file_name = "db_ok.csv"
        db.file_name = file_name
        l = {'date': datetime.strptime('2023-04-05T12:00:00', '%Y-%m-%dT%H:%M:%S'), 'did_water': False, 'moisture': 12000}
        db.write_line(l)
        with open(file_name, 'r') as fr:
            lines = fr.read().splitlines()
        assert lines[-1] == '2023-04-05T12:00:00,0,12000'

