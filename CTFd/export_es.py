import sqlite3
import csv
import schedule
import time
from elasticsearch import helpers, Elasticsearch
import pandas as pd


def export():
    DB = "CTFd/ctfd.db"
    # Users
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * from Users")
    result = cur.fetchall()
    cur.execute("SELECT name FROM pragma_table_info('users')")

    headerList = cur.fetchall()
    with open('user.csv', 'w', newline='') as csvfile:
        c = csv.writer(csvfile, delimiter=',')
        c.writerow(headerList)
        for x in result:
            c.writerow(x)
    
    # Votes
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * from Votes")
    result = cur.fetchall()
    cur.execute("SELECT name FROM pragma_table_info('votes')")

    headerList = cur.fetchall()
    with open('vote.csv', 'w', newline='') as csvfile:
        c = csv.writer(csvfile, delimiter=',')
        c.writerow(headerList)
        for x in result:
            c.writerow(x)

    # Challenges
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * from Challenges")
    result = cur.fetchall()
    cur.execute("SELECT name FROM pragma_table_info('challenges')")

    headerList = cur.fetchall()
    with open('challenge.csv', 'w', newline='') as csvfile:
        c = csv.writer(csvfile, delimiter=',')
        c.writerow(headerList)
        for x in result:
            c.writerow(x)

    # Solves
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * from Solves")
    result = cur.fetchall()
    cur.execute("SELECT name FROM pragma_table_info('solves')")

    headerList = cur.fetchall()
    with open('solve.csv', 'w', newline='') as csvfile:
        c = csv.writer(csvfile, delimiter=',')
        c.writerow(headerList)
        for x in result:
            c.writerow(x)

    # Submission
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * from Submissions")
    result = cur.fetchall()
    cur.execute("SELECT name FROM pragma_table_info('submissions')")

    headerList = cur.fetchall()
    with open('submission.csv', 'w', newline='') as csvfile:
        c = csv.writer(csvfile, delimiter=',')
        c.writerow(headerList)
        for x in result:
            c.writerow(x)

    #Tags
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * from Tags")
    result = cur.fetchall()
    cur.execute("SELECT name FROM pragma_table_info('tags')")

    headerList = cur.fetchall()
    with open('tag.csv', 'w', newline='') as csvfile:
        c = csv.writer(csvfile, delimiter=',')
        c.writerow(headerList)
        for x in result:
            c.writerow(x)

    #TagChallenge
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * from TagChallenge")
    result = cur.fetchall()
    cur.execute("SELECT name FROM pragma_table_info('tagChallenge')")

    headerList = cur.fetchall()
    with open('tagChallenge.csv', 'w', newline='') as csvFile:
        c = csv.writer(csvFile, delimiter=',')
        c.writerow(headerList)
        for x in result:
            c.writerow(x)


    # Merge Submissions and Challenges

    sub = pd.read_csv("submission.csv", sep=',')
    chal = pd.read_csv("challenge.csv", sep=',')

    challenge = chal.rename(columns = {"('id',)":"('challenge_id',)"})

    challenge = challenge.drop(columns = ["('type',)",], axis = 1)

    submission = sub.set_index("('challenge_id',)")
    challenges = challenge.set_index("('challenge_id',)")

    dfMixedChalSub = submission.join(challenges)

    dfMixedChalSub.to_csv("chal&sub.csv", sep=',')

    #Merge Submissions and Users

    user = pd.read_csv("user.csv", sep=',', encoding = "ISO-8859-1")
    user = user.rename(columns = {"('id',)":"('user_id',)"})
    user = user.drop(columns = ["('type',)",], axis = 1)

    submission = sub.set_index("('user_id',)")
    users = user.set_index("('user_id',)")

    dfMixedUserSub = submission.join(users)

    dfMixedUserSub.to_csv("user&sub.csv", sep=',')
    
    #Merge Tag et TagChallenge

    tag = pd.read_csv("tag.csv", sep=',', encoding='latin-1')
    tagchal = pd.read_csv("tagChallenge.csv", sep=',', encoding='latin-1')

    tags = tag.rename(columns = {"('id',)":"('tag_id',)"})

    tagChallenge = tagchal.set_index("('tag_id',)")
    tagss = tags.set_index("('tag_id',)")

    dfMixedTagChal = tagChallenge.join(tagss)

    dfMixedTagChal.to_csv("merge_tagchal.csv", sep=',')
    
    #Connection ES

    es = Elasticsearch()
    with open('submission.csv') as f:
        reader = csv.DictReader(f)
        if es.indices.exists(index="submission"):
            es.indices.delete(index='submission')
        helpers.bulk(es, reader, index='submission', doc_type='my-type')

    with open('solve.csv') as f:
        reader = csv.DictReader(f)
        if es.indices.exists(index="solve"):
            es.indices.delete(index='solve')
        helpers.bulk(es, reader, index='solve', doc_type='my-type')

    with open('challenge.csv') as f:
        reader = csv.DictReader(f)
        if es.indices.exists(index="challenge"):
            es.indices.delete(index='challenge')
        helpers.bulk(es, reader, index='challenge', doc_type='my-type')

    with open('vote.csv') as f:
        reader = csv.DictReader(f)
        if es.indices.exists(index="vote"):
            es.indices.delete(index='vote')
        helpers.bulk(es, reader, index='vote', doc_type='my-type')

    with open('user.csv') as f:
        reader = csv.DictReader(f)
        if es.indices.exists(index="user"):
            es.indices.delete(index='user')
        helpers.bulk(es, reader, index='user', doc_type='my-type')
    
    with open('chal&sub.csv') as f:
        reader = csv.DictReader(f)
        if es.indices.exists(index="chal&sub"):
            es.indices.delete(index='chal&sub')
        helpers.bulk(es, reader, index='chal&sub', doc_type='my-type')

    with open('user&sub.csv') as f:
        reader = csv.DictReader(f)
        if es.indices.exists(index="user&sub"):
            es.indices.delete(index='user&sub')
        helpers.bulk(es, reader, index='user&sub', doc_type='my-type')
    
    with open('merge_tagchal.csv') as f:
        reader = csv.DictReader(f)
        if es.indices.exists(index="merge_tagchal"):
            es.indices.delete(index='merge_tagchal')
        helpers.bulk(es, reader, index='merge_tagchal', doc_type='my-type')
    

    print("Data updated")

export()
schedule.every(1).minutes.do(export)

while 1:
    schedule.run_pending()
    time.sleep(1)
