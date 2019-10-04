import chardet
import pandas as pd
import sqlite3
import pytz

local = pytz.timezone('Asia/Kolkata')

conn = sqlite3.connect("db.sqlite3")

curr = conn.cursor()


with open("TblMeterChange.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('TblMeterChange.csv', encoding=result['encoding'])

d.drop(columns=['SNo', 'Change_No', 'UsrName'], inplace=True)

d.columns = ['dt', 'flat_id', 'amt_left', 'old_meter_sr',
       'old_start_eb', 'old_start_dg', 'old_ng_eb',
       'old_ng_dg', 'old_last_eb', 'old_last_dg',
       'new_meter_sr', 'new_start_eb', 'new_start_dg']

d.index.name = 'id'

d.index += 1

d['dt'] = pd.to_datetime(d['dt'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(local).dt.tz_convert(pytz.utc)

#d.to_sql('users_meterchange', conn, if_exists="append")

#conn.commit()'''
