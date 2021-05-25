from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import db, TagChallenge, Tags
from CTFd.schemas.tag_challenge import TagChallengeSchema
from CTFd.utils.decorators import access_granted_only
from CTFd.utils.user import has_right
from CTFd.utils.helpers.models import build_model_filters

tag_challenge_namespace = Namespace("tag_challenge", description="Endpoint to retrieve TagChallenge")

TagChallengeModel = sqlalchemy_to_pydantic(TagChallenge)


class TagChallengeDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: TagChallengeModel


class TagChallengeListSuccessResponse(APIListSuccessResponse):
    data: List[TagChallengeModel]


tag_challenge_namespace.schema_model(
    "TagChallengeDetailedSuccessResponse", TagChallengeDetailedSuccessResponse.apidoc()
)

tag_challenge_namespace.schema_model("TagChallengeListSuccessResponse", TagChallengeListSuccessResponse.apidoc())


@tag_challenge_namespace.route("")
class TagChallengeList(Resource):
    @access_granted_only("api_tag_challenge_list_get")
    @tag_challenge_namespace.doc(
        description="Endpoint to list Tag objects in bulk",
        responses={
            200: ("Success", "TagChallengeListSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
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
                    "TagFields", 
                    {
                        "tag_id": "tagId",
                        "challenge_id": "challengeId"
                    }
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

        tag_challenge = TagChallenge.query.filter_by(**query_args).filter(*filters).all()
        schema = TagChallengeSchema(many=True)
        response = schema.dump(tag_challenge)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_tag_challenge_list_post")
    @tag_challenge_namespace.doc(
        description="Endpoint to create a TagChallenge object",
        responses={
            200: ("Success", "TagChallengeDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = TagChallengeSchema()
        response = schema.load(req, session=db.session)

        tag_challenges = TagChallenge.query.filter_by(challenge_id=response.data.challenge_id).all()
        tag = Tags.query.filter_by(id=response.data.tag_id).first()

        # Check if the challenge already has an exercise tag
        if tag.exercise is True:
            # If a contributor try to add an exercise tag, return an error
            if has_right("api_tag_challenge_list_post_restricted"):
                return {"success": False, "error": "notAllowed"}
            # If there is already an exercise tag assigned, return an error
            for tag_challenge in tag_challenges:
                tag_already_assigned = Tags.query.filter_by(id=tag_challenge.tag_id).first()
                if tag_already_assigned.exercise is True:
                    return {"success": False, "error": "alreadyAssigned"}

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@tag_challenge_namespace.route("/<tag_id>/<challenge_id>")
@tag_challenge_namespace.param("tag_id", "A Tag ID")
@tag_challenge_namespace.param("challenge_id", "A challenge ID")
class TagChal(Resource):
    @access_granted_only("api_tag_challenge_get")
    @tag_challenge_namespace.doc(
        description="Endpoint to get a specific TagChallenge object",
        responses={
            200: ("Success", "TagChallengeDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, tag_id, challenge_id):
        tag_challenge = TagChallenge.query.filter_by(tag_id=tag_id, challenge_id=challenge_id).first_or_404()

        response = TagChallengeSchema().dump(tag_challenge)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    
    @access_granted_only("api_tag_challenge_delete")
    @tag_challenge_namespace.doc(
        description="Endpoint to delete a specific TagChallenge object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, tag_id, challenge_id):
        tag_challenge = TagChallenge.query.filter_by(tag_id=tag_id, challenge_id=challenge_id).first_or_404()
        nb_of_challenges_belonging_to_tag = len(TagChallenge.query.filter_by(tag_id=tag_id).all())

        if nb_of_challenges_belonging_to_tag == 1:
            # If there is only one challenge linked to this tag ID,
            # we delete it, and the link with the challenge will be 
            # deleted too.
            db.session.delete(Tags.query.filter_by(id=tag_id).first_or_404())
        else:
            db.session.delete(tag_challenge) 

        db.session.commit()
        db.session.close()

        return {"success": True}
