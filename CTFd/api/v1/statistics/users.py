from flask_restx import Resource
from sqlalchemy import func

from CTFd.api.v1.statistics import statistics_namespace
from CTFd.models import Users
from CTFd.utils.modes import get_model
from CTFd.utils.decorators import teachers_admins_only


@statistics_namespace.route("/users")
class UserStatistics(Resource):
    @teachers_admins_only
    def get(self):
        registered = Users.query.count()
        confirmed = Users.query.filter_by(verified=True).count()
        data = {"registered": registered, "confirmed": confirmed}
        return {"success": True, "data": data}


@statistics_namespace.route("/users/<column>")
class UserPropertyCounts(Resource):
    @teachers_admins_only
    def get(self, column):
        if column in Users.__table__.columns.keys():
            prop = getattr(Users, column)
            data = (
                Users.query.with_entities(prop, func.count(prop)).group_by(prop).all()
            )
            return {"success": True, "data": dict(data)}
        else:
            return {"success": False, "message": "That could not be found"}, 404

""" @statistics_namespace.route("/users/percentages")
class UserPercentages(Resource):
    @teacehrs_admins_only
    def get(self):
        users = (
            Users.query.add_columns("id","school")
            .all()
        )

        Model = get_model()

        total_users = (
            db.session.query(Users.account_id)
            .join(Model)
            .filter(Model.banned == False, Model.hidden == False)
            .group_by(Users.account_id)
            .count()
        )

        percentage_data = []
        for user in users:
            user_count = (
                Users.query.join(Model, Users.account_id == Model.id)
                .filter(
                    Users.school == user.school,
                    Model.banned == False,
                    Model.hidden == False,
                )
                .count()
            )

            percentage = float(user_count) / float(total_users)

            percentage_data.append(
                {"school": user.school, "percentage":percentage}
            )

        response = sorted(percentage_data, key=lambda x: x["percentage"], reverse=True)
        return {"success": True, "data": response}
 """