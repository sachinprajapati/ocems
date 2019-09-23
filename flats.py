import chardet
import pandas as pd
import sqlite3

conn = sqlite3.connect("db.sqlite3")

curr = conn.cursor()


with open("totalflats.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('totalflats.csv', encoding=result['encoding'])

d.drop(columns=['SNo', 'Field_Name', 'Field_Amt', 'Unnamed: 0'], inplace=True)


d.columns = ['id', 'flat', 'tower', 'flat_size', 'owner', 'profession', 'status', 'phone', 'email', 'meter_sr', 'basis', 'fixed_amt']

d.set_index('id', inplace=True)

d.loc[d['status'] == "Occupied", 'status'] = 1

d.loc[d['status'] == "Vacant", 'status'] = 2

d.loc[d['basis'] == "N", 'basis'] = 1

d.loc[d['basis'] == "Y", 'basis'] = 2

d.to_sql('users_flats', conn, if_exists='append')

conn.commit()
