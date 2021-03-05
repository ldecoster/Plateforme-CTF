from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import db, TagChallenge, Tags
from CTFd.schemas.tags import TagSchema
from CTFd.utils.decorators import access_granted_only
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.user import has_right

tags_namespace = Namespace("tags", description="Endpoint to retrieve Tags")

TagModel = sqlalchemy_to_pydantic(Tags)


class TagDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: TagModel


class TagListSuccessResponse(APIListSuccessResponse):
    data: List[TagModel]


tags_namespace.schema_model(
    "TagDetailedSuccessResponse", TagDetailedSuccessResponse.apidoc()
)

tags_namespace.schema_model("TagListSuccessResponse", TagListSuccessResponse.apidoc())


@tags_namespace.route("")
class TagList(Resource):
    @tags_namespace.doc(
        description="Endpoint to list Tag objects in bulk",
        responses={
            200: ("Success", "TagListSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @access_granted_only("api_tag_list_get")
    @validate_args(
        {
            "value": (str, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "TagFields", {"value": "value"}
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Tags, query=q, field=field)

        tags = Tags.query.filter_by(**query_args).filter(*filters).all()
        schema = TagSchema(many=True)
        response = schema.dump(tags)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_tag_list_post")
    @tags_namespace.doc(
        description="Endpoint to create a Tag object",
        responses={
            200: ("Success", "TagDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = TagSchema()
        response = schema.load(req, session=db.session)

        tag_challenges = TagChallenge.query.filter_by(challenge_id=req.get("challenge_id")).all()

        # Only for contributors
        if has_right("api_tag_list_post_restricted"):
            if "ex" in response.data.value:
                return {"success": False, "error": "notAllowed"}

        # Check if the challenge already has an exercise tag
        if "ex" in response.data.value:
            for tag_challenge in tag_challenges:
                tag = Tags.query.filter_by(id=tag_challenge.tag_id).first()
                if "ex" in tag.value:
                    return {"success": False, "error": "alreadyAssigned"}

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@tags_namespace.route("/<tag_id>")
@tags_namespace.param("tag_id", "A Tag ID")
class Tag(Resource):
    @access_granted_only("api_tag_get")
    @tags_namespace.doc(
        description="Endpoint to get a specific Tag object",
        responses={
            200: ("Success", "TagDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()

        response = TagSchema().dump(tag)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_tag_patch")
    @tags_namespace.doc(
        description="Endpoint to edit a specific Tag object",
        responses={
            200: ("Success", "TagDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        schema = TagSchema()
        req = request.get_json()

        # TODO ISEN : vérifier utilité de la ligne ci-dessous
        tag.value = req["tagValue"]

        response = schema.load(req, session=db.session, instance=tag)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

    @access_granted_only("api_tag_delete")
    @tags_namespace.doc(
        description="Endpoint to delete a specific Tag object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        tag_challenges = TagChallenge.query.filter_by(tag_id=tag.id).all()

        for t in tag_challenges:
            db.session.delete(t)

        db.session.delete(tag)
        db.session.commit()
        db.session.close()

        return {"success": True}
