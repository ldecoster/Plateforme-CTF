import sqlite3
import csv 
from elasticsearch import helpers, Elasticsearch

DB = "ctfd.db"
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

###Submission
conn = sqlite3.connect(DB)
cur=conn.cursor()
cur.execute("SELECT * from Submissions")
result=cur.fetchall()
cur.execute("SELECT name FROM pragma_table_info('submissions')")

headerList = cur.fetchall()
c = csv.writer(open('submission.csv', 'w',newline=''), delimiter = ',')
c.writerow(headerList)
for x in result:
    c.writerow(x)

es = Elasticsearch()
with open('submission.csv') as f:
    reader = csv.DictReader(f)
    helpers.bulk(es, reader, index='submission', doc_type='my-type')

with open('solve.csv') as f:
    reader = csv.DictReader(f)
    helpers.bulk(es, reader, index='solve', doc_type='my-type')

with open('challenge.csv') as f:
    reader = csv.DictReader(f)
    helpers.bulk(es, reader, index='challenge', doc_type='my-type')

with open('vote.csv') as f:
    reader = csv.DictReader(f)
    helpers.bulk(es, reader, index='vote', doc_type='my-type')

with open('user.csv') as f:
    reader = csv.DictReader(f)
    helpers.bulk(es, reader, index='user', doc_type='my-type')