from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import db, TagChallenge
from CTFd.schemas.tagChallenge import TagChallengeSchema
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers.models import build_model_filters
tagChallenge_namespace = Namespace("tagChallenge", description="Endpoint to retrieve TagChallenge")

TagChallengeModel = sqlalchemy_to_pydantic(TagChallenge)


class TagChallengeDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: TagChallengeModel


class TagChallengeListSuccessResponse(APIListSuccessResponse):
    data: List[TagChallengeModel]


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

        tagChallenge = TagChallenge.query.filter_by(**query_args).filter(*filters).all()
        schema = TagChallengeSchema(many=True)
        response = schema.dump(tags)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @tagChallenge_namespace.doc(
        description="Endpoint to create a TagChallenge object",
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


@tagChallenge_namespace.route("/<tag_id>/<challenge_id>")
@tagChallenge_namespace.param("tag_id", "A Tag ID")
@tagChallenge_namespace.param("challenge_id", "A challenge ID")
class TagChal(Resource):
    @admins_only
    @tagChallenge_namespace.doc(
        description="Endpoint to delete a specific TagChallenge object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self,tag_id,challenge_id):
        print("****DELETE METHODE CALLED*****")
        tagChallenge = TagChallenge.query.filter_by(tag_id=tag_id,challenge_id=challenge_id).first_or_404()
        db.session.delete(tagChallenge)
        db.session.commit()
        db.session.close()

        return {"success": True}