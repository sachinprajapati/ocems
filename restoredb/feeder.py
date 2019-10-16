import chardet
import pandas as pd
import pytz
from sqlalchemy import create_engine

conn = create_engine('postgresql://sachin:admin123@localhost:5432/ocems')

local = pytz.timezone('Asia/Kolkata')

with open("TblFeeder.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('TblFeeder.csv', encoding=result['encoding'])

d.drop(columns=['SNo', 'Feeder_Pkey'], inplace=True)

d.columns = ['ps_key', 'name', 'desc', 'eb', 'dg', 'load', 'f_type']

d.index.name = 'id'

d.index += 1

d.to_sql('users_feeder', conn, if_exists="append")