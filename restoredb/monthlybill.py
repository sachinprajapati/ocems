import chardet
import pandas as pd
import sqlite3
import pytz

local = pytz.timezone('Asia/Kolkata')

conn = sqlite3.connect("db.sqlite3")

curr = conn.cursor()


with open("TblMonthlyBill.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('TblMonthlyBill.csv', encoding=result['encoding'])

d.drop(columns=['Bill_Pkey',], inplace=True)

d.columns = ['flat_id', 'month', 'year', 'start_eb', 'start_dg',
       'end_eb', 'end_dg', 'opn_amt', 'cls_amt', 'eb_price',
       'dg_price', 'start_dt', 'end_dt']

d.index.name = 'id'

d.index += 1

d['start_dt'] = pd.to_datetime(d['start_dt'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(local).dt.tz_convert(pytz.utc)

d['end_dt'] = pd.to_datetime(d['end_dt'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(local).dt.tz_convert(pytz.utc)

d.to_sql('users_monthlybill', conn, if_exists="append")

conn.commit()
