import chardet
import pandas as pd
import sqlite3
import pytz

local = pytz.timezone('Asia/Kolkata')

conn = sqlite3.connect("db.sqlite3")

curr = conn.cursor()


with open("TblConsumption.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('TblConsumption.csv', encoding=result['encoding'])

d.drop(columns=['SNo', 'Tower_No', 'Flat_No','Recharge_Amt','Msg_Status', 'RowVersion', 'SIM_Msg_Status', 'Ref_Utility_KWH', 'Ref_DG_KWH'], inplace=True)


d.columns = ['datetime', 'flat_id', 'eb',
       'dg', 'amt_left',
       'start_eb', 'start_dg', 'status',
       'reset_dt', 'meter_change_dt',
       'last_modified', 'last_deduction_dt', 'deduction_status',
       'ng_eb', 'ng_dg', 'ng_dt']


d['datetime'] = pd.to_datetime(d['datetime'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(local).dt.tz_convert(pytz.utc)

d['ng_dt'] = pd.to_datetime(d['ng_dt'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(local).dt.tz_convert(pytz.utc)

d['last_deduction_dt'] = pd.to_datetime(d['last_deduction_dt'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(local).dt.tz_convert(pytz.utc)

d.index.name = 'id'

d.index += 1

d.loc[d['deduction_status'] == "N", ['deduction_status']] = 1

d.loc[d['deduction_status'] == "Y", ['deduction_status']] = 2

d.to_sql('users_consumption', conn, if_exists="append")

conn.commit()
