import chardet
import pandas as pd
import sqlite3

conn = sqlite3.connect("db.sqlite3")

curr = conn.cursor()


with open("TblReadings.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('TblReadings.csv', encoding=result['encoding'])

d.drop(columns=['Recharge_Amt', 'Field_Amt', 'Status'], inplace=True)

d.columns = ['dt', 'flat_id', 'eb', 'dg', 'ref_eb',
       'ref_dg', 'amt_left', 'eb_price', 'dg_price',
       'mrate', 'famt']

d.index.name = 'id'

d.index += 1


d.to_sql('users_reading', conn, if_exists="append")

conn.commit()
