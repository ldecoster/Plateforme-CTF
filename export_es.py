from CTFd import create_app
from elasticsearch import helpers, Elasticsearch
from CTFd.utils import get_app_config

import csv
import glob
import os
import pandas as pd
import schedule
import sqlite3
import time
import uuid


def export():
    app = create_app()
    with app.app_context():
        # Generate temp folder from uploads
        upload_folder = get_app_config("UPLOAD_FOLDER")
        random_name = uuid.uuid4().hex
        upload_folder_name = upload_folder + '/' + random_name + '/'
        os.mkdir(upload_folder_name)

        db = get_app_config("SQLALCHEMY_DATABASE_URI").replace("sqlite:///", "")
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        # Users
        cur.execute("SELECT * from users")
        result = cur.fetchall()
        cur.execute("SELECT name FROM pragma_table_info('users')")
        header_list = cur.fetchall()

        with open(upload_folder_name + 'user.csv', 'w', newline='', encoding='utf-8') as csv_file:
            c = csv.writer(csv_file, delimiter=',')
            c.writerow(header_list)
            for x in result:
                c.writerow(x)

        # Votes
        cur.execute("SELECT * from votes")
        result = cur.fetchall()
        cur.execute("SELECT name FROM pragma_table_info('votes')")
        header_list = cur.fetchall()

        with open(upload_folder_name + 'vote.csv', 'w', newline='', encoding='utf-8') as csv_file:
            c = csv.writer(csv_file, delimiter=',')
            c.writerow(header_list)
            for x in result:
                c.writerow(x)

        # Challenges
        cur.execute("SELECT * from challenges")
        result = cur.fetchall()
        cur.execute("SELECT name FROM pragma_table_info('challenges')")
        header_list = cur.fetchall()

        with open(upload_folder_name + 'challenge.csv', 'w', newline='', encoding='utf-8') as csv_file:
            c = csv.writer(csv_file, delimiter=',')
            c.writerow(header_list)
            for x in result:
                c.writerow(x)

        # Solves
        cur.execute("SELECT * from solves")
        result = cur.fetchall()
        cur.execute("SELECT name FROM pragma_table_info('solves')")
        header_list = cur.fetchall()

        with open(upload_folder_name + 'solve.csv', 'w', newline='', encoding='utf-8') as csv_file:
            c = csv.writer(csv_file, delimiter=',')
            c.writerow(header_list)
            for x in result:
                c.writerow(x)

        # Submission
        cur.execute("SELECT * from submissions")
        result = cur.fetchall()
        cur.execute("SELECT name FROM pragma_table_info('submissions')")
        header_list = cur.fetchall()

        with open(upload_folder_name + 'submission.csv', 'w', newline='', encoding='utf-8') as csv_file:
            c = csv.writer(csv_file, delimiter=',')
            c.writerow(header_list)
            for x in result:
                c.writerow(x)

        # Tags
        cur.execute("SELECT * from tags")
        result = cur.fetchall()
        cur.execute("SELECT name FROM pragma_table_info('tags')")
        header_list = cur.fetchall()

        with open(upload_folder_name + 'tag.csv', 'w', newline='', encoding='utf-8') as csv_file:
            c = csv.writer(csv_file, delimiter=',')
            c.writerow(header_list)
            for x in result:
                c.writerow(x)

        # TagChallenge
        cur.execute("SELECT * from tagChallenge")
        result = cur.fetchall()
        cur.execute("SELECT name FROM pragma_table_info('tagChallenge')")
        header_list = cur.fetchall()

        with open(upload_folder_name + 'tagChallenge.csv', 'w', newline='', encoding='utf-8') as csvFile:
            c = csv.writer(csvFile, delimiter=',')
            c.writerow(header_list)
            for x in result:
                c.writerow(x)

        # Closing connection
        conn.close()

        # Merge Submissions and Challenges
        sub = pd.read_csv(upload_folder_name + "submission.csv", sep=',')
        chal = pd.read_csv(upload_folder_name + "challenge.csv", sep=',')

        challenge = chal.rename(columns={"('id',)": "('challenge_id',)"})

        challenge = challenge.drop(columns=["('type',)", ], axis=1)

        submission = sub.set_index("('challenge_id',)")
        challenges = challenge.set_index("('challenge_id',)")

        df_mixed_chal_sub = submission.join(challenges)

        df_mixed_chal_sub.to_csv(upload_folder_name + "chal&sub.csv", sep=',')

        # Merge Submissions and Users
        user = pd.read_csv(upload_folder_name + "user.csv", sep=',', encoding='utf-8')
        user = user.rename(columns={"('id',)": "('user_id',)"})
        user = user.drop(columns=["('type',)", ], axis=1)

        submission = sub.set_index("('user_id',)")
        users = user.set_index("('user_id',)")

        df_mixed_user_sub = submission.join(users)

        df_mixed_user_sub.to_csv(upload_folder_name + "user&sub.csv", sep=',')

        # Merge Tag and TagChallenge
        tag = pd.read_csv(upload_folder_name + "tag.csv", sep=',', encoding='utf-8')
        tagchal = pd.read_csv(upload_folder_name + "tagChallenge.csv", sep=',', encoding='utf-8')

        tags = tag.rename(columns={"('id',)": "('tag_id',)"})

        tagChallenge = tagchal.set_index("('tag_id',)")
        tagss = tags.set_index("('tag_id',)")

        df_mixed_tag_chal = tagChallenge.join(tagss)

        df_mixed_tag_chal.to_csv(upload_folder_name + "merge_tagchal.csv", sep=',')

        # ES connection
        es = Elasticsearch()
        with open(upload_folder_name + 'submission.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if es.indices.exists(index="submission"):
                es.indices.delete(index='submission')
            helpers.bulk(es, reader, index='submission', doc_type='my-type')

        with open(upload_folder_name + 'solve.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if es.indices.exists(index="solve"):
                es.indices.delete(index='solve')
            helpers.bulk(es, reader, index='solve', doc_type='my-type')

        with open(upload_folder_name + 'challenge.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if es.indices.exists(index="challenge"):
                es.indices.delete(index='challenge')
            helpers.bulk(es, reader, index='challenge', doc_type='my-type')

        with open(upload_folder_name + 'vote.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if es.indices.exists(index="vote"):
                es.indices.delete(index='vote')
            helpers.bulk(es, reader, index='vote', doc_type='my-type')

        with open(upload_folder_name + 'user.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if es.indices.exists(index="user"):
                es.indices.delete(index='user')
            helpers.bulk(es, reader, index='user', doc_type='my-type')

        with open(upload_folder_name + 'chal&sub.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if es.indices.exists(index="chal&sub"):
                es.indices.delete(index='chal&sub')
            helpers.bulk(es, reader, index='chal&sub', doc_type='my-type')

        with open(upload_folder_name + 'user&sub.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if es.indices.exists(index="user&sub"):
                es.indices.delete(index='user&sub')
            helpers.bulk(es, reader, index='user&sub', doc_type='my-type')

        with open(upload_folder_name + 'merge_tagchal.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if es.indices.exists(index="merge_tagchal"):
                es.indices.delete(index='merge_tagchal')
            helpers.bulk(es, reader, index='merge_tagchal', doc_type='my-type')

        # Remove files and folder
        files = glob.glob(upload_folder_name + '*')
        for file in files:
            os.remove(file)
        os.rmdir(upload_folder_name)
        print("Data updated")


export()
schedule.every(1).minutes.do(export)

while 1:
    schedule.run_pending()
    time.sleep(1)
