import chardet
import pandas as pd
import sqlite3

conn = sqlite3.connect("db.sqlite3")

curr = conn.cursor()


with open("TblRecharge.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('TblRecharge.csv', encoding=result['encoding'])

d.drop(columns=['Recharge_No', 'RPT_Chq_DD', 'Chq_DD_Date', 'UsrName', 'Recharge_TYPE'], inplace=True)

d.columns = ['sno', 'dt', 'flat_id', 'amt_left', 'recharge',
       'Type', 'chq_dd', 'eb', 'dg']

d.index.name = 'id'

d.index += 1


d.to_sql('users_recharge', conn, if_exists="append")

conn.commit()
