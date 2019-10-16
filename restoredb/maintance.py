import chardet
import pandas as pd
import pytz

from sqlalchemy import create_engine

conn = create_engine('postgresql://sachin:admin123@localhost:5432/ocems')

local = pytz.timezone('Asia/Kolkata')

with open("TblMaintenance.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('TblMaintenance.csv', encoding=result['encoding'])

d.drop(columns=['SNo', 'Flat_Size', 'Field_Amt'], inplace=True)

d.columns = ['dt', 'mrate', 'mcharge', 'flat_id', 'famt']

d.index.name = 'id'

d.index += 1

d['dt'] = pd.to_datetime(d['dt'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize(local).dt.tz_convert(pytz.utc)

d.drop(d.loc[d['flat_id'] == 950].index, inplace=True)
d.drop(d.loc[d['flat_id'] == 840].index, inplace=True)

print("to sql")
#d.to_sql('users_maintance', conn, if_exists="append")
