from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Badges, db
from CTFd.schemas.badges import BadgeSchema
from CTFd.utils.decorators import access_granted_only
from CTFd.utils.helpers.models import build_model_filters

badges_namespace = Namespace("badges", description="Endpoint to retrieve Badges")

BadgeModel = sqlalchemy_to_pydantic(Badges)


class BadgeDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: BadgeModel


class BadgeListSuccessResponse(APIListSuccessResponse):
    data: List[BadgeModel]


badges_namespace.schema_model(
    "BadgeDetailedSuccessResponse", BadgeDetailedSuccessResponse.apidoc()
)

badges_namespace.schema_model(
    "BadgeListSuccessResponse", BadgeListSuccessResponse.apidoc()
)


@badges_namespace.route("")
class BadgeList(Resource):
    @access_granted_only("api_badge_list_get")
    @badges_namespace.doc(
        description="Endpoint to list Badge objects in bulk",
        responses={
            200: ("Success", "BadgeListSuccessResponse"),
            400: (
                    "An error occurred processing the provided or stored data",
                    "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "description": (str, None),
            "name": (str, None),
            "tag_id": (int, None),
            "q": (str, None),
            "field": (
                    RawEnum(
                        "BadgeFields",
                        {
                            "description": "description",
                            "name": "name",
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
        filters = build_model_filters(model=Badges, query=q, field=field)

        badges = Badges.query.filter_by(**query_args).filter(*filters).all()
        schema = BadgeSchema(many=True)
        response = schema.dump(badges)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_badge_list_post")
    @badges_namespace.doc(
        description="Endpoint to create a Badge object",
        responses={
            200: ("Success", "BadgeListSuccessResponse"),
            400: (
                    "An error occurred processing the provided or stored data",
                    "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = BadgeSchema()

        response = schema.load(req, session=db.session)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@badges_namespace.route("/<badge_id>")
@badges_namespace.param("badge_id", "A Badge ID")
class Badge(Resource):
    @access_granted_only("api_badge_get")
    @badges_namespace.doc(
        description="Endpoint to get a specific Badge object",
        responses={
            200: ("Success", "BadgeDetailedSuccessResponse"),
            400: (
                    "An error occurred processing the provided or stored data",
                    "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, badge_id):
        badge = Badges.query.filter_by(id=badge_id).first_or_404()
        response = BadgeSchema().dump(badge)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_badge_patch")
    @badges_namespace.doc(
        description="Endpoint to patch a Badge object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def patch(self, badge_id):
        badge = Badges.query.filter_by(id=badge_id).first_or_404()
        schema = BadgeSchema()
        req = request.get_json()

        response = schema.load(req, session=db.session, instance=badge, partial=True)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

    @access_granted_only("api_badge_delete")
    @badges_namespace.doc(
        description="Endpoint to delete a Badge object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, badge_id):
        badge = Badges.query.filter_by(id=badge_id).first_or_404()
        db.session.delete(badge)
        db.session.commit()
        db.session.close()

        return {"success": True}
