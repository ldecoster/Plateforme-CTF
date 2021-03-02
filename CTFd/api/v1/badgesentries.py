from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import BadgesEntries, Users, db
from CTFd.schemas.badgesentries import BadgesEntriesSchema
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers.models import build_model_filters

badges_entries_namespace = Namespace("badges_entries", description="Endpoint to retrieve user's badges")

BadgeEntriesModel = sqlalchemy_to_pydantic(BadgesEntries)


class BadgesEntriesDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: BadgeEntriesModel


class BadgesEntriesListSuccessResponse(APIListSuccessResponse):
    data: List[BadgeEntriesModel]


badges_entries_namespace.schema_model(
    "BadgesEntriesDetailedSuccessResponse", BadgesEntriesDetailedSuccessResponse.apidoc()
)

badges_entries_namespace.schema_model(
    "BadgesEntriesListSuccessResponse", BadgesEntriesListSuccessResponse.apidoc()
)


@badges_entries_namespace.route("")
class BadgesList(Resource):
    @admins_only
    @badges_entries_namespace.doc(
        description="Endpoint to list BadgesEntries objects in bulk",
        responses={
            200: ("Success", "BadgesEntriesListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "user_id": (int, None),
            "type": (str, None),
            "icon": (int, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "BadgesEntriesFields",
                    {
                        "name": "name",
                        "description": "description",
                        "icon": "icon",
                    },
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=BadgesEntries, query=q, field=field)

        badges_entries = BadgesEntries.query.filter_by(**query_args).filter(*filters).all()
        schema = BadgesEntriesSchema(many=True)
        response = schema.dump(badges_entries)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @badges_entries_namespace.doc(
        description="Endpoint to create an BadgesEntries object",
        responses={
            200: ("Success", "BadgesEntriesListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()

        schema = BadgesEntriesSchema()

        response = schema.load(req, session=db.session)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()


        return {"success": True, "data": response.data}


@badges_entries_namespace.route("/<badges_entries_id>")
@badges_entries_namespace.param("badges_entries_id", "An BadgesEntries ID")
class BadgesEntries(Resource):
    @admins_only
    @badges_entries_namespace.doc(
        description="Endpoint to get a specific BadgesEntries object",
        responses={
            200: ("Success", "BadgesEntriesDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, badges_entries_id):
        badges_entries = BadgesEntries.query.filter_by(id=badges_entries_id).first_or_404()
        response = BadgesEntriesSchema().dump(badges_entries)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @badges_entries_namespace.doc(
        description="Endpoint to delete an BadgesEntries object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, badges_entries_id):
        badgesentries = BadgesEntries.query.filter_by(id=badges_entries_id).first_or_404()
        db.session.delete(badgesentries)
        db.session.commit()
        db.session.close()


        return {"success": True}
