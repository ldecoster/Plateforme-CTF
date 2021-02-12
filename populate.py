#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import hashlib
import random
import argparse

from CTFd import create_app
from CTFd.cache import clear_config, clear_pages
from CTFd.models import (
    Users,
    Challenges,
    Flags,
    Awards,
    ChallengeFiles,
    Fails,
    Solves,
    Tracking,
    Votes,
)
from faker import Faker

fake = Faker()

parser = argparse.ArgumentParser()

parser.add_argument("--mode", help="Set user mode", default="users")
parser.add_argument("--users", help="Amount of users to generate", default=50, type=int)
parser.add_argument(
    "--challenges", help="Amount of challenges to generate", default=20, type=int
)
parser.add_argument(
    "--awards", help="Amount of awards to generate", default=5, type=int
)

args = parser.parse_args()

app = create_app()

mode = args.mode
USER_AMOUNT = args.users
CHAL_AMOUNT = args.challenges
AWARDS_AMOUNT = args.awards

icons = [
    None,
    "shield",
    "bug",
    "crown",
    "crosshairs",
    "ban",
    "lightning",
    "code",
    "cowboy",
    "angry",
]

school = ["ISA", "ISEN", "HEI"]

speciality_ISEN = [
    "Big Data",
    "Objets Connectés",
    "Electronique Embarqué",
    "Robotique mobile",
    "Ingénierie d'affaires",
    "Finance",
    "Cybersécurité",
    "Développement Logiciel",
    "Nanosciences"
]

speciality_ISA = [
    "Agriculture",
    "Agroalimentaire",
    "Environnement",
    "Agroéconomie",
    "Entrepreneuriat"
]

speciality_HEI = [
    "TP",
    "Architecture",
    "Management d'entreprise",
    "Conception Mécanique",
    "Energies",
    "Médicale et Santé",
    "Informatique",
    "Chimie",
    "Smart Cities",
    "Innovation et Management textile",
    "Entrepreneuriat",
    "Management opé industrielles et logostiques",
    "Mécatronique et robotique"
]

companies = ["Corp", "Inc.", "Squad", "Team"]


def gen_sentence():
    return fake.text()


def gen_name():
    return fake.first_name()


def gen_email():
    return fake.email()


def gen_value():
    return random.choice(range(100, 500, 50))


def gen_word():
    return fake.word()


def gen_icon():
    return random.choice(icons)


def gen_file():
    return fake.file_name()


def gen_ip():
    return fake.ipv4()


def gen_affiliation():
    return (fake.word() + " " + random.choice(companies)).title()


def random_date(start, end):
    return start + datetime.timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )


def random_chance():
    return random.random() > 0.5


def gen_school():
    return random.choice(school)


def gen_speciality_ISEN():
    return random.choice(speciality_ISEN)


def gen_speciality_ISA():
    return random.choice(speciality_ISA)


def gen_speciality_HEI():
    return random.choice(speciality_HEI)


if __name__ == "__main__":
    with app.app_context():
        db = app.db

        # Generating Users
        print("GENERATING USERS")
        used = []
        count = 0
        while count < USER_AMOUNT:
            name = gen_name()
            if name not in used:
                used.append(name)
                try:
                    user = Users(name=name, email=gen_email(), password="password")
                    user.school = gen_school()
                    user.promotion = random.randint(62,66)

                    if user.school == "ISEN":
                        user.speciality = gen_speciality_ISEN()
                    if user.school == "ISA" : 
                        user.speciality = gen_speciality_ISA()
                    if user.school == "HEI":
                        user.speciality = gen_speciality_HEI()

                    user.verified = True
                    if random_chance():
                        user.affiliation = gen_affiliation()
                    db.session.add(user)
                    db.session.flush()

                    track = Tracking(ip=gen_ip(), user_id=user.id)
                    db.session.add(track)
                    db.session.flush()
                    count += 1
                except Exception:
                    pass

        db.session.commit()

        # Generating Challenges
        print("GENERATING CHALLENGES")
        for x in range(CHAL_AMOUNT):
            word = gen_word()
            user = random.randint(1,USER_AMOUNT)
            chal = Challenges(
                name=word,
                description=gen_sentence(),
                author_id=user,
            )
            db.session.add(chal)
            db.session.commit()
            f = Flags(challenge_id=x + 1, content=word, type="static")
            db.session.add(f)
            db.session.commit()

        # Generating Files
        print("GENERATING FILES")
        AMT_CHALS_WITH_FILES = int(CHAL_AMOUNT * (3.0 / 4.0))
        for x in range(AMT_CHALS_WITH_FILES):
            chal = random.randint(1, CHAL_AMOUNT)
            filename = gen_file()
            md5hash = hashlib.md5(filename.encode("utf-8")).hexdigest()
            chal_file = ChallengeFiles(
                challenge_id=chal, location=md5hash + "/" + filename
            )
            db.session.add(chal_file)

        db.session.commit()
       

        #Generating Votes
        print("GENERATING VOTES")
        if mode == "users":
         for x in range(USER_AMOUNT):
                used = []
                base_time = datetime.datetime.utcnow() + datetime.timedelta(
                    minutes=-10000
                )
                for y in range(random.randint(1, CHAL_AMOUNT)):
                    chalid = random.randint(1, CHAL_AMOUNT)
                    if chalid not in used:
                        used.append(chalid)
                        user = Users.query.filter_by(id=x + 1).first()
                        vot = Votes(
                            challenge_id=chalid,
                            user_id=user.id,
                            value=random.randint(0,1),
                        )
                        new_base = random_date(
                            base_time,
                            base_time
                            + datetime.timedelta(minutes=random.randint(30, 60)),
                        )
                        vot.date = new_base
                        base_time = new_base

                        db.session.add(vot)
                        db.session.commit()


        # Generating Solves
        print("GENERATING SOLVES")
        if mode == "users":
            for x in range(USER_AMOUNT):
                used = []
                base_time = datetime.datetime.utcnow() + datetime.timedelta(
                    minutes=-10000
                )
                for y in range(random.randint(1, CHAL_AMOUNT)):
                    chalid = random.randint(1, CHAL_AMOUNT)
                    if chalid not in used:
                        used.append(chalid)
                        user = Users.query.filter_by(id=x + 1).first()
                        solve = Solves(
                            user_id=user.id,
                            challenge_id=chalid,
                            ip="127.0.0.1",
                            provided=gen_word(),
                        )

                        new_base = random_date(
                            base_time,
                            base_time
                            + datetime.timedelta(minutes=random.randint(30, 60)),
                        )
                        solve.date = new_base
                        base_time = new_base

                        db.session.add(solve)
                        db.session.commit()
    
        db.session.commit()
        

        # Generating Awards
        print("GENERATING AWARDS")
        for x in range(USER_AMOUNT):
            base_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=-10000)
            for _ in range(random.randint(0, AWARDS_AMOUNT)):
                user = Users.query.filter_by(id=x + 1).first()
                award = Awards(
                    user_id=user.id,
                    name=gen_word(),
                    icon=gen_icon(),
                )
                new_base = random_date(
                    base_time,
                    base_time + datetime.timedelta(minutes=random.randint(30, 60)),
                )
                award.date = new_base
                base_time = new_base

                db.session.add(award)

        db.session.commit()

        # Generating Wrong Flags
        print("GENERATING WRONG FLAGS")
        for x in range(USER_AMOUNT):
            used = []
            base_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=-10000)
            for y in range(random.randint(1, CHAL_AMOUNT * 20)):
                chalid = random.randint(1, CHAL_AMOUNT)
                if chalid not in used:
                    used.append(chalid)
                    user = Users.query.filter_by(id=x + 1).first()
                    wrong = Fails(
                        user_id=user.id,
                        challenge_id=chalid,
                        ip="127.0.0.1",
                        provided=gen_word(),
                    )

                    new_base = random_date(
                        base_time,
                        base_time + datetime.timedelta(minutes=random.randint(30, 60)),
                    )
                    wrong.date = new_base
                    base_time = new_base

                    db.session.add(wrong)
                    db.session.commit()

        db.session.commit()
        db.session.close()

        clear_config()
        clear_pages()
