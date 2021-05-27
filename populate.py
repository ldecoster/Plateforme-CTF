#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import hashlib
import random
import argparse

from CTFd import create_app
from CTFd.cache import clear_config, clear_pages
from CTFd.models import (
    Badges,
    ChallengeFiles,
    Challenges,
    Fails,
    Flags,
    Solves,
    TagChallenge,
    Tags,
    Tracking,
    Users,
    Votes,
)
from faker import Faker

fake = Faker()

parser = argparse.ArgumentParser()

parser.add_argument("--users", help="Amount of users to generate", default=50, type=int)
parser.add_argument("--challenges", help="Amount of challenges to generate", default=20, type=int)
parser.add_argument("--badges", help="Amount of badges to generate", default=5, type=int)
parser.add_argument("--tags", help="Amount of tags to generate", default=4, type=int)

args = parser.parse_args()

app = create_app()

USER_AMOUNT = args.users
CHALLENGE_AMOUNT = args.challenges
BADGES_AMOUNT = args.badges
TAGS_AMOUNT = args.tags

school = ["ISA", "ISEN", "HEI"]

specialisation_ISEN = [
    "RCMOC",
    "SNE",
    "IAMN",
    "RM",
    "DLBDCC",
    "BD",
    "TMS",
    "BE",
    "BN",
    "NM",
    "CS",
    "IA",
    "DSD",
    "FN",
    "ME",
    "EN",
    "SE",
    "NEDD"
]

specialisation_ISA = [
    "AGI",
    "AGO",
    "ENV",
    "MKT"
]

specialisation_HEI = [
    "BTP",
    "BAA",
    "MEOF",
    "CM",
    "ESEA",
    "IMS",
    "ITI",
    "CITE",
    "SC",
    "TIMT",
    "EIE",
    "MOIL",
    "MR"
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


def gen_file():
    return fake.file_name()


def gen_ip():
    return fake.ipv4()


def random_date(start, end):
    return start + datetime.timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )


def random_chance():
    return random.random() > 0.5


def gen_school():
    return random.choice(school)


def gen_specialisation_ISEN():
    return random.choice(specialisation_ISEN)


def gen_specialisation_ISA():
    return random.choice(specialisation_ISA)


def gen_specialisation_HEI():
    return random.choice(specialisation_HEI)


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

                    if user.school == "ISEN":
                        user.specialisation = gen_specialisation_ISEN()
                    if user.school == "ISA":
                        user.specialisation = gen_specialisation_ISA()
                    if user.school == "HEI":
                        user.specialisation = gen_specialisation_HEI()

                    user.verified = True
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
        for x in range(CHALLENGE_AMOUNT):
            word = gen_word()
            user = random.randint(1, USER_AMOUNT)
            challenge = Challenges(
                name=word,
                description=gen_sentence(),
                author_id=user,
            )
            db.session.add(challenge)
            db.session.commit()
            f = Flags(challenge_id=x + 1, content=word, type="static")
            db.session.add(f)
            db.session.commit()

        # Generating Files
        print("GENERATING FILES")
        AMT_CHALS_WITH_FILES = int(CHALLENGE_AMOUNT * (3.0 / 4.0))
        for x in range(AMT_CHALS_WITH_FILES):
            challenge = random.randint(1, CHALLENGE_AMOUNT)
            filename = gen_file()
            md5hash = hashlib.md5(filename.encode("utf-8")).hexdigest()
            challenge_file = ChallengeFiles(
                challenge_id=challenge, location=md5hash + "/" + filename
            )
            db.session.add(challenge_file)

        db.session.commit()

        # Generating Votes
        print("GENERATING VOTES")
        for x in range(USER_AMOUNT):
            used = []
            base_time = datetime.datetime.utcnow() + datetime.timedelta(
                minutes=-10000
            )
            for y in range(random.randint(1, CHALLENGE_AMOUNT)):
                challenge_id = random.randint(1, CHALLENGE_AMOUNT)
                if challenge_id not in used:
                    used.append(challenge_id)
                    user = Users.query.filter_by(id=x + 1).first()
                    vot = Votes(
                        challenge_id=challenge_id,
                        user_id=user.id,
                        value=bool(random.randint(0, 1)),
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
        for x in range(USER_AMOUNT):
            used = []
            base_time = datetime.datetime.utcnow() + datetime.timedelta(
                minutes=-10000
            )
            for y in range(random.randint(1, CHALLENGE_AMOUNT)):
                challenge_id = random.randint(1, CHALLENGE_AMOUNT)
                if challenge_id not in used:
                    used.append(challenge_id)
                    user = Users.query.filter_by(id=x + 1).first()
                    solve = Solves(
                        user_id=user.id,
                        challenge_id=challenge_id,
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

        # Generating Tags
        print("GENERATING TAGS")
        tags = []
        for x in range(TAGS_AMOUNT):
            tags.append(gen_word())
            tag = Tags(
                value=tags[x],
                exercise=bool(random.randint(0, 1))
            )
           
            db.session.add(tag)

        db.session.commit()

        # Generating Tag Challenge
        print("GENERATING TAG CHALLENGE")
        for x in range(CHALLENGE_AMOUNT):
            used = []
            base_time = datetime.datetime.utcnow() + datetime.timedelta(
                minutes=-10000
            )
            for y in range(random.randint(1, TAGS_AMOUNT)):
                tag_id = random.randint(1, len(tags))
                if tag_id not in used:
                    used.append(tag_id)
                    challenge = Challenges.query.filter_by(id=x + 1).first()
                    tag_challenge = TagChallenge(
                        challenge_id=challenge.id,
                        tag_id=tag_id,
                    )

                    new_base = random_date(
                        base_time,
                        base_time
                        + datetime.timedelta(minutes=random.randint(30, 60)),
                    )
                    tag_challenge.date = new_base
                    base_time = new_base

                    db.session.add(tag_challenge)
                    db.session.commit()
    
        db.session.commit()

        # Generating Badges
        print("GENERATING BADGES")
        for x in range(BADGES_AMOUNT):
            random_int = random.randint(1, BADGES_AMOUNT)
            tag = Tags.query.filter_by(id=random_int).first()
            if tag is not None and tag.exercise is True:
                badge = Badges(
                    name=gen_word(),
                    description=gen_sentence(),
                    tag_id=tag.id
                )
                db.session.add(badge)

        db.session.commit()

        # Generating Wrong Flags
        print("GENERATING WRONG FLAGS")
        for x in range(USER_AMOUNT):
            used = []
            base_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=-10000)
            for y in range(random.randint(1, CHALLENGE_AMOUNT * 20)):
                challenge_id = random.randint(1, CHALLENGE_AMOUNT)
                if challenge_id not in used:
                    used.append(challenge_id)
                    user = Users.query.filter_by(id=x + 1).first()
                    wrong = Fails(
                        user_id=user.id,
                        challenge_id=challenge_id,
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
