import sqlite3
import csv 

DB = "CTFd/ctfd.db"

conn = sqlite3.connect(DB)
cur=conn.cursor()
cur.execute("SELECT * from Users")
result=cur.fetchall()
cur.execute("SELECT name FROM pragma_table_info('users')")

headerList = cur.fetchall()
c = csv.writer(open('data.csv', 'w',newline=''), delimiter = ';')
c.writerow(headerList)
for x in result:
    c.writerow(x)