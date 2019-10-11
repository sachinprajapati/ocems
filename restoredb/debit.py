import chardet
import pandas as pd
import sqlite3
import pytz

local = pytz.timezone('Asia/Kolkata')

conn = sqlite3.connect("db.sqlite3")

curr = conn.cursor()


with open("TblDebit.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('TblDebit.csv', encoding=result['encoding'])

d.drop(columns=['SNo','Debit_No', 'Category', 'Rpt_TYPE', 'RPT_Chq_DD', 'Chq_DD_No', 'Chq_DD_Date', 'UsrName'], inplace=True)

d.columns = ['dt', 'flat_id', 'amt_left', 'debit_amt', 'eb', 'dg', 'remarks']

d.index.name = 'id'

d.index += 1

d['dt'] = pd.to_datetime(d['dt'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(local).dt.tz_convert(pytz.utc)

d.to_sql('users_debit', conn, if_exists="append")

conn.commit()
