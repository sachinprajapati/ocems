import chardet
import pandas as pd
import sqlite3
import pytz

local = pytz.timezone('Asia/Kolkata')

conn = sqlite3.connect("db.sqlite3")

curr = conn.cursor()


with open("TblFeeder.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('TblFeeder.csv', encoding=result['encoding'])

d.drop(columns=['SNo', 'Feeder_Pkey'], inplace=True)

d.columns = ['ps_key', 'name', 'desc', 'eb', 'dg', 'load', 'f_type']

d.index.name = 'id'

d.index += 1

d.to_sql('users_feeder', conn, if_exists="append")

conn.commit()
