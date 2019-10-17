import chardet
import pandas as pd
import pytz
from sqlalchemy import create_engine

conn = create_engine('postgresql://sachin:admin123@localhost:5432/ocems')
local = pytz.timezone('Asia/Kolkata')

with open("TblRecharge.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('TblRecharge.csv', encoding=result['encoding'])

d.drop(columns=['SNo', 'Recharge_No', 'RPT_Chq_DD', 'Chq_DD_Date', 'UsrName', 'Recharge_TYPE'], inplace=True)

d.columns = ['dt', 'flat_id', 'amt_left', 'recharge',
       'Type', 'chq_dd', 'eb', 'dg']

d.index.name = 'id'

d.index += 1

d['dt'] = pd.to_datetime(d['dt'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(local).dt.tz_convert(pytz.utc)

d.loc[d['Type'].str.lower() == "cash", ['Type']] = 1
d.loc[d['Type'].str.lower() == "neft", ['Type']] = 3
d.loc[d.query("Type != 1 and Type != 3").index, ['Type']] = 2

d.drop(d.loc[d['flat_id'] == 950].index, inplace=True)
d.to_sql('users_recharge', conn, if_exists="append")
