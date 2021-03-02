from flask_restx import Resource
from sqlalchemy import func
from sqlalchemy.sql import and_

from CTFd.api.v1.statistics import statistics_namespace
from CTFd.models import Challenges, Solves, Users, db
from CTFd.utils.decorators import admins_only
from CTFd.utils.modes import get_model


@statistics_namespace.route("/challenges/<column>")
class ChallengePropertyCounts(Resource):
    @admins_only
    def get(self, column):
        if column in Challenges.__table__.columns.keys():
            prop = getattr(Challenges, column)
            data = (
                Challenges.query.with_entities(prop, func.count(prop))
                .group_by(prop)
                .all()
            )
            return {"success": True, "data": dict(data)}
        else:
            response = {"message": "That could not be found"}, 404
            return response


@statistics_namespace.route("/challenges/solves")
class ChallengeSolveStatistics(Resource):
    @admins_only
    def get(self):
        chals = (
            Challenges.query.filter(
                and_(Challenges.state != "hidden", Challenges.state != "locked")
            )
            .all()
        )

        Model = get_model()

        solves_sub = (
            db.session.query(
                Solves.challenge_id, db.func.count(Solves.challenge_id).label("solves")
            )
            .join(Model, Solves.account_id == Model.id)
            .filter(Model.banned == False, Model.hidden == False)
            .group_by(Solves.challenge_id)
            .subquery()
        )

        solves = (
            db.session.query(
                solves_sub.columns.challenge_id,
                solves_sub.columns.solves,
                Challenges.name,
            )
            .join(Challenges, solves_sub.columns.challenge_id == Challenges.id)
            .all()
        )

        response = []
        has_solves = []

        for challenge_id, count, name in solves:
            challenge = {"id": challenge_id, "name": name, "solves": count}
            response.append(challenge)
            has_solves.append(challenge_id)
        for c in chals:
            if c.id not in has_solves:
                challenge = {"id": c.id, "name": c.name, "solves": 0}
                response.append(challenge)

        db.session.close()
        return {"success": True, "data": response}


@statistics_namespace.route("/challenges/solves/percentages")
class ChallengeSolvePercentages(Resource):
    @admins_only
    def get(self):
        challenges = (
            Challenges.query.add_columns("id", "name", "state", "max_attempts")
            .all()
        )

        Model = get_model()

        number_of_users = (
            Users.query
            .filter(
                Model.banned == False,
                Model.hidden == False,
            )
            .count()
        )

        percentage_data = []
        for challenge in challenges:
            solve_count = (
                Solves.query.join(Model, Solves.account_id == Model.id)
                .filter(
                    Solves.challenge_id == challenge.id,
                    Model.banned == False,
                    Model.hidden == False,
                )
                .count()
            )

            if number_of_users == 0:
                percentage = 0
            else:
                percentage = float(solve_count) / float(number_of_users)

            percentage_data.append(
                {"id": challenge.id, "name": challenge.name, "percentage": percentage}
            )

        response = sorted(percentage_data, key=lambda x: x["percentage"], reverse=True)
        return {"success": True, "data": response}
