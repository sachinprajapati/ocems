import chardet
import pandas as pd
import sqlite3
from sqlalchemy import create_engine

conn = create_engine('postgresql://sachin:admin123@localhost:5432/ocems')

with open("TblTower.csv", 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large


d = pd.read_csv('TblTower.csv', encoding=result['encoding'])

d.drop(columns=['SNo', 'Field_Name', 'Field_Amt'], inplace=True)

d.columns = ['tower', 'tower_name', 'eb_price', 'dg_price', 'maintance',
       'fixed_amt']

d.index.name = 'id'

d.index += 1


d.to_sql('users_deductionamt', conn, if_exists="append")
