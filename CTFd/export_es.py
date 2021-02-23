import sqlite3
import csv 

DB = "CTFd/ctfd.db"
###Users
conn = sqlite3.connect(DB)
cur=conn.cursor()
cur.execute("SELECT * from Users")
result=cur.fetchall()
cur.execute("SELECT name FROM pragma_table_info('users')")

headerList = cur.fetchall()
c = csv.writer(open('user.csv', 'w',newline=''), delimiter = ';')
c.writerow(headerList)
for x in result:
    c.writerow(x)
###Votes
conn = sqlite3.connect(DB)
cur=conn.cursor()
cur.execute("SELECT * from Votes")
result=cur.fetchall()
cur.execute("SELECT name FROM pragma_table_info('votes')")

headerList = cur.fetchall()
c = csv.writer(open('vote.csv', 'w',newline=''), delimiter = ';')
c.writerow(headerList)
for x in result:
    c.writerow(x)

###Challenges
conn = sqlite3.connect(DB)
cur=conn.cursor()
cur.execute("SELECT * from Challenges")
result=cur.fetchall()
cur.execute("SELECT name FROM pragma_table_info('challenges')")

headerList = cur.fetchall()
c = csv.writer(open('challenge.csv', 'w',newline=''), delimiter = ';')
c.writerow(headerList)
for x in result:
    c.writerow(x)

###Solves
conn = sqlite3.connect(DB)
cur=conn.cursor()
cur.execute("SELECT * from Solves")
result=cur.fetchall()
cur.execute("SELECT name FROM pragma_table_info('solves')")

headerList = cur.fetchall()
c = csv.writer(open('solve.csv', 'w',newline=''), delimiter = ',')
c.writerow(headerList)
for x in result:
    c.writerow(x)