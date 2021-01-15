#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import hashlib
import random
import argparse

from CTFd import create_app
from CTFd.cache import clear_config, clear_standings, clear_pages
from CTFd.models import (
    Users,
    Challenges,
    Exercices,
    Flags,
    BadgesEntries,
    BadgesExercices,
    ChallengeFiles,
    Fails,
    Solves,
    Tracking,
    Votes,
    Badges
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
    "--badgesentries", help="Amount of badgesentries to generate", default=5, type=int
)

parser.add_argument(
    "--badges", help="Amount of badges to generate", default=5, type=int
)

parser.add_argument(
    "--exercices", help="Amount of exercices to generate", default=20, type=int
)

args = parser.parse_args()

app = create_app()

mode = args.mode
USER_AMOUNT = args.users
CHAL_AMOUNT = args.challenges
BADGE_AMOUNT = args.badges
EXER_AMOUNT = args.exercices


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

badges = ["Forensic I", "Forensic II", "Forensic III", "Badge I", "Badge II", "Badge 3", "Badge 4"]


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

def gen_badge():
    return random.choice(badges)

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
        used_oauth_ids = []
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
                    if random_chance():
                        oauth_id = random.randint(1, 1000)
                        while oauth_id in used_oauth_ids:
                            oauth_id = random.randint(1, 1000)
                        used_oauth_ids.append(oauth_id)
                        user.oauth_id = oauth_id
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
       
        # Generating Exercices 
        print("GENERATING EXERCICES")
        for x in range (EXER_AMOUNT):
            id = random.randint(0,10000)
            if id not in used:
                used.append(id)
                word = gen_word()
                exer = Exercices(
                    id=id,
                    name=word,
                    description=gen_sentence()
                )


                db.session.add(exer)
                db.session.commit()

        #Generating Badges
        print("GENERATING BADGES")
        if mode == "users":
         for x in range(BADGE_AMOUNT):
                used = []
                base_time = datetime.datetime.utcnow() + datetime.timedelta(
                    minutes=-10000
                )
                for y in range(random.randint(1, BADGE_AMOUNT)):
                    id = random.randint(0,10000)
                    if id not in used:
                        used.append(id)
                        # user = Users.query.filter_by(id=x + 1).first()
                        badge = Badges(
                            id = id,
                            description = "test desc",
                            name= gen_badge(),
                        )
                        new_base = random_date(
                            base_time,
                            base_time
                            + datetime.timedelta(minutes=random.randint(30, 60)),
                        )

                        base_time = new_base

                        db.session.add(badge)
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
        

        # Generating Badges Entries
        print("GENERATING BADGESENTRIES")
        for x in range(USER_AMOUNT):
            base_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=-10000)
            for _ in range(random.randint(0, BADGE_AMOUNT)):
                user = Users.query.filter_by(id=x + 1).first()
                badgesentries = BadgesEntries(
                    user_id=user.id,
                    badge_id=badge.id,
                )
                new_base = random_date(
                    base_time,
                    base_time + datetime.timedelta(minutes=random.randint(30, 60)),
                )
                BadgesEntries.date = new_base
                base_time = new_base
                db.session.add(badgesentries)
                db.session.commit()


        #Generating Badges Exercices
        print("GENERATING BADGESEXERCICES")
        for x in range(BADGE_AMOUNT):
             base_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=-10000)
             for _ in range(random.randint(0, BADGE_AMOUNT)):
                 user = Users.query.filter_by(id=x + 1).first()
                 badgesexercice = BadgesExercices(
                     exercice_id = exer.id,
                     badge_id = badge.id,
                 )
                 new_base = random_date(
                     base_time,
                     base_time + datetime.timedelta(minutes=random.randint(30, 60)),
                 )
                 BadgesExercices.date = new_base
                 base_time = new_base

                 db.session.add(badgesexercice)
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
        clear_standings()
        clear_pages()
