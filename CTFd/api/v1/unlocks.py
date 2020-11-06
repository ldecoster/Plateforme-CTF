from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.cache import clear_standings
from CTFd.constants import RawEnum
from CTFd.models import Unlocks, db, get_class_by_tablename
from CTFd.schemas.badgesentries import BadgesEntriesSchema
from CTFd.schemas.unlocks import UnlockSchema
from CTFd.utils.decorators import (
    admins_only,
    authed_only,
    during_ctf_time_only,
    require_verified_emails,
)
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.user import get_current_user

unlocks_namespace = Namespace("unlocks", description="Endpoint to retrieve Unlocks")

UnlockModel = sqlalchemy_to_pydantic(Unlocks)
TransientUnlockModel = sqlalchemy_to_pydantic(Unlocks, exclude=["id"])


class UnlockDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: UnlockModel


class UnlockListSuccessResponse(APIListSuccessResponse):
    data: List[UnlockModel]


unlocks_namespace.schema_model(
    "UnlockDetailedSuccessResponse", UnlockDetailedSuccessResponse.apidoc()
)

unlocks_namespace.schema_model(
    "UnlockListSuccessResponse", UnlockListSuccessResponse.apidoc()
)


@unlocks_namespace.route("")
class UnlockList(Resource):
    @admins_only
    @unlocks_namespace.doc(
        description="Endpoint to get unlock objects in bulk",
        responses={
            200: ("Success", "UnlockListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "user_id": (int, None),
            "team_id": (int, None),
            "target": (int, None),
            "type": (str, None),
            "q": (str, None),
            "field": (
                RawEnum("UnlockFields", {"target": "target", "type": "type"}),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Unlocks, query=q, field=field)

        unlocks = Unlocks.query.filter_by(**query_args).filter(*filters).all()
        schema = UnlockSchema()
        response = schema.dump(unlocks)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @during_ctf_time_only
    @require_verified_emails
    @authed_only
    @unlocks_namespace.doc(
        description="Endpoint to create an unlock object. Used to unlock hints.",
        responses={
            200: ("Success", "UnlockDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        user = get_current_user()

        req["user_id"] = user.id
        req["team_id"] = user.team_id

        Model = get_class_by_tablename(req["type"])
        target = Model.query.filter_by(id=req["target"]).first_or_404()

        if target.cost > user.score:
            return (
                {
                    "success": False,
                    "errors": {
                        "score": "You do not have enough points to unlock this hint"
                    },
                },
                400,
            )

        schema = UnlockSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        existing = Unlocks.query.filter_by(**req).first()
        if existing:
            return (
                {
                    "success": False,
                    "errors": {"target": "You've already unlocked this this target"},
                },
                400,
            )

        db.session.add(response.data)

        badges_entries_schema = BadgesEntriesSchema()
        badges_entries = {
            "user_id": user.id,
            #"team_id": user.team_id,
            "name": target.name,
            "description": target.description,
            "value": (-target.cost),
            "category": target.category,
        }

        badges_entries = badges_entries_schema.load(badges_entries)
        db.session.add(badges_entries.data)
        db.session.commit()
        clear_standings()

        response = schema.dump(response.data)

        return {"success": True, "data": response.data}
