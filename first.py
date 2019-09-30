from bottle import route, run, template, HTTPResponse
import pyodbc
import json

try:
    conn = pyodbc.connect(
    "Driver={SQL Server};"
    #"Server=DESKTOP-6H8OE2G\WINCCFLEX2014;"
    "Server=SACHIN-PC;"
    "Database=EMS;"
    "Trusted_Connection=yes;"
    )
except Exception as e:
    print(e)
    conn = None

cur = conn.cursor()

@route('/hello/<name>')
def index(name):
    a = cur.execute("select [Flat_Pkey], [Utility_KWH],[DG_KWH]  from [TblConsumption]")
    l = []
    c = a.fetchall()
    for i in c:
        l.append({"flat_id": i[0], "eb": i[1], "dg": i[2]})
    context = {
        "data": name,
        "sql": l
        }
    return HTTPResponse(context)

run(host='localhost', port=8080)
