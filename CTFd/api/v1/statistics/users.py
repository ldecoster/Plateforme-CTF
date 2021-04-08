from flask_restx import Resource
from sqlalchemy import func

from CTFd.api.v1.statistics import statistics_namespace
from CTFd.models import Users
from CTFd.utils.decorators import access_granted_only


@statistics_namespace.route("/users")
class UserStatistics(Resource):
    @access_granted_only("api_statistics_user_statistics_get")
    def get(self):
        registered = Users.query.count()
        confirmed = Users.query.filter_by(verified=True).count()
        data = {"registered": registered, "confirmed": confirmed}
        return {"success": True, "data": data}


@statistics_namespace.route("/users/<column>")
class UserPropertyCounts(Resource):
    @access_granted_only("api_statistics_user_property_counts_get")
    def get(self, column):
        if column in Users.__table__.columns.keys():
            prop = getattr(Users, column)
            data = (
                Users.query.with_entities(prop, func.count(prop)).group_by(prop).all()
            )
            return {"success": True, "data": dict(data)}
        else:
            return {"success": False, "message": "That could not be found"}, 404
