import csv
from datetime import datetime, timedelta
from datetime import datetime
from pathlib import Path

from rfirr.config import config
from rfirr.service import str_to_date, date_to_str

if not config.test_mode:
    file_name = config.outside_db['file_path']
else:
    file_name = 'db_test_rfirr.csv'

header = list(config.outside_db['columns'].keys())

def instantiate_db():
    Path(file_name).touch(exist_ok=True)
    with open(file_name, 'r') as fp:
        lines = fp.read().splitlines()
    hdrstr = ','.join(header)
    if not lines:
        with open(file_name, 'w') as fp:
            fp.write(f"{hdrstr}\n")
        return
    if lines[0] != hdrstr:
        raise ValueError(f"CSV database header missing or malformed: {lines[0]}")

def get_dtypes():
    dtypes = dict()
    raw_dtypes = config.outside_db['columns']
    for rd, rt in raw_dtypes.items():
        t = None
        if rt == 'datetime':
            t = datetime
        elif rt == 'bool':
            t = bool
        elif rt == 'int':
            t = int
        elif rt == 'float':
            t = float
        elif rt in ['str', 'string', 'text']:
            t = str
        if not t:
            raise ValuError(f"Could not map {rt} to a type, please change config")
        dtypes[rd] = t
    return dtypes

def convert_types(record: dict):
    res = record.copy()
    for column_name, val in record.items():
        dtype = dtypes[column_name]
        if dtype == datetime:
            res[column_name] = str_to_date(val)
        elif dtype == bool:
            res[column_name] = dtype(int(val))
        else:
            res[column_name] = dtype(val)
    return res

def filter_date(
        recordset: csv.DictReader,
        start:str|datetime,
        end:str|datetime
    ):
    res = []
    if isinstance(start, str):
        start = str_to_date(start)
    if isinstance(end, str):
        end = str_to_date(end)
    for r in recordset:
        d = str_to_date(r['date'])
        if end:
            if d > start and d < end:
                res.append(r)
        else:
            if d > start:
                res.append(r)
    return res

def read(
        start_date: str,
        end_date: str | None = None
    ):
    with open(file_name, 'r') as fr:
        reader = csv.DictReader(fr)
        res = filter_date(reader, start_date, end_date)
        res = [convert_types(x) for x in res]
    return res

def write_line(line: dict):
    '''All values need to be correct python types'''
    to_write = line.copy()
    for k,v in line.items():
        dtype = dtypes[k]
        if dtype == datetime:
            to_write[k] = date_to_str(v)
        elif dtype == bool:
            if v == False:
                to_write[k] = '0'
            elif v == True:
                to_write[k] = '1'
            else:
                raise ValueError(f"Written boolean needs to be python boolean, got {v}({type(v)})")
    with open(file_name, 'a') as fw:
        writer = csv.DictWriter(
            fw,
            fieldnames = header,
        )
        writer.writerow(to_write)

dtypes = get_dtypes()
instantiate_db()
