from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import TagChallenge, db
from CTFd.schemas.tagChallenge import TagChallengeSchema
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers.models import build_model_filters
tagChallenge_namespace = Namespace("tagChallenge", description="Endpoint to retrieve Tags")

TagChallenge = sqlalchemy_to_pydantic(TagChallenge)


class TagChallengeDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: TagChallenge


class TagChallengeListSuccessResponse(APIListSuccessResponse):
    data: List[TagChallenge]


tagChallenge_namespace.schema_model(
    "TagChallengeDetailedSuccessResponse", TagChallengeDetailedSuccessResponse.apidoc()
)

tagChallenge_namespace.schema_model("TagChallengeListSuccessResponse", TagChallengeListSuccessResponse.apidoc())


@tagChallenge_namespace.route("")
class TagChallengeList(Resource):
    @admins_only
    @tagChallenge_namespace.doc(
        description="Endpoint to list Tag objects in bulk",
        responses={
            200: ("Success", "TagChallengeListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "challenge_id": (int, None),
            "tag_id": (int, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "TagFields", {"challenge_id": "challenge_id", "tag_id": "tag_id"}
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=TagChallenge, query=q, field=field)

        tagChallenge = TagChallenge.query.filter_by(**query_args).filter(*filters).all()
        schema = TagChallengeSchema(many=True)
        response = schema.dump(tags)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @tagChallenge_namespace.doc(
        description="Endpoint to create a Tag object",
        responses={
            200: ("Success", "TagChallengeDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = TagChallengeSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

@tags_namespace.route("/<tagChallenge_id>")
@tags_namespace.param("tagChallenge_id", "A TagChallenge ID")
class TagChallenge(Resource):
    @admins_only
    @tags_namespace.doc(
        description="Endpoint to get a specific TagChallenge object",
        responses={
            200: ("Success", "TagDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, tagChallenge_id):
        tagChallenge = TagChallenge.query.filter_by(id=tagChallenge_id).first_or_404()

        response = TagChallengeSchema().dump(tagChallenge)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @tagChallenge_namespace.doc(
        description="Endpoint to edit a specific Tag object",
        responses={
            200: ("Success", "TagDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, tagChallenge_id):
        tag = TagChallenge.query.filter_by(id=tagChallenge_id).first_or_404()
        schema = TagChallengeSchema()
        req = request.get_json()

        response = schema.load(req, session=db.session, instance=tag)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

    @admins_only
    @tagChallenge_namespace.doc(
        description="Endpoint to delete a specific Tag object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, tagChallenge_id):
        tag = TagChallenge.query.filter_by(id=tagChallenge_id).first_or_404()
        db.session.delete(tag)
        db.session.commit()
        db.session.close()

        return {"success": True}