import chardet
import pandas as pd
import sqlite3

conn = sqlite3.connect("db.sqlite3")

curr = conn.cursor()


with open("TblMonthlyBill.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('TblMonthlyBill.csv', encoding=result['encoding'])

d.columns = ['Bill_Pkey', 'flat_id', 'month', 'year', 'start_eb', 'start_dg',
       'end_eb', 'end_dg', 'opn_amt', 'cls_amt', 'eb_price',
       'dg_price', 'start_dt', 'end_dt']

d.index.name = 'id'

d.index += 1


d.to_sql('users_monthlybill', conn, if_exists="append")

conn.commit()
