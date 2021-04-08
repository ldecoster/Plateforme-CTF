from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Challenges, Hints, db
from CTFd.schemas.hints import HintSchema
from CTFd.utils.decorators import access_granted_only, authed_only
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.user import has_right_or_is_author

hints_namespace = Namespace("hints", description="Endpoint to retrieve Hints")

HintModel = sqlalchemy_to_pydantic(Hints)


class HintDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: HintModel


class HintListSuccessResponse(APIListSuccessResponse):
    data: List[HintModel]


hints_namespace.schema_model(
    "HintDetailedSuccessResponse", HintDetailedSuccessResponse.apidoc()
)

hints_namespace.schema_model(
    "HintListSuccessResponse", HintListSuccessResponse.apidoc()
)


@hints_namespace.route("")
class HintList(Resource):
    @access_granted_only("api_hint_list_get")
    @hints_namespace.doc(
        description="Endpoint to list Hint objects in bulk",
        responses={
            200: ("Success", "HintListSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "type": (str, None),
            "challenge_id": (int, None),
            "content": (str, None),
            "q": (str, None),
            "field": (
                RawEnum("HintFields", {"type": "type", "content": "content"}),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Hints, query=q, field=field)

        hints = Hints.query.filter_by(**query_args).filter(*filters).all()
        response = HintSchema(many=True, view="locked").dump(hints)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_hint_list_post")
    @hints_namespace.doc(
        description="Endpoint to create a Hint object",
        responses={
            200: ("Success", "HintDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = HintSchema(view="admin")
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        if has_right_or_is_author("api_hint_list_post", response.data.challenge.author_id):
            db.session.commit()

            response = schema.dump(response.data)

            return {"success": True, "data": response.data}
        return {"success": False}


@hints_namespace.route("/<hint_id>")
class Hint(Resource):
    @authed_only
    @hints_namespace.doc(
        description="Endpoint to get a specific Hint object",
        responses={
            200: ("Success", "HintDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()

        response = HintSchema(view="unlocked").dump(hint)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_hint_patch")
    @hints_namespace.doc(
        description="Endpoint to edit a specific Hint object",
        responses={
            200: ("Success", "HintDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        challenge = Challenges.query.filter_by(id=hint.challenge_id).first_or_404()
        if has_right_or_is_author("api_hint_patch", challenge.author_id):
            req = request.get_json()

            schema = HintSchema(view="admin")
            response = schema.load(req, instance=hint, partial=True, session=db.session)

            if response.errors:
                return {"success": False, "errors": response.errors}, 400

            db.session.add(response.data)
            db.session.commit()

            response = schema.dump(response.data)

            return {"success": True, "data": response.data}
        return {"success": False}

    @access_granted_only("api_hint_delete")
    @hints_namespace.doc(
        description="Endpoint to delete a specific Tag object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        challenge = Challenges.query.filter_by(id=hint.challenge_id).first_or_404()
        if has_right_or_is_author("api_hint_delete", challenge.author_id):
            db.session.delete(hint)
            db.session.commit()
            db.session.close()

            return {"success": True}
        return {"success": False}
