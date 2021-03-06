from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Votes, db, Challenges
from CTFd.schemas.votes import VoteSchema
from CTFd.utils.decorators import access_granted_only
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.user import has_right
from flask import session

votes_namespace = Namespace("votes", description="Endpoint to retrieve Votes")

VoteModel = sqlalchemy_to_pydantic(Votes)


class VoteDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: VoteModel


class VoteListSuccessResponse(APIListSuccessResponse):
    data: List[VoteModel]


votes_namespace.schema_model(
    "VoteDetailedSuccessResponse", VoteDetailedSuccessResponse.apidoc()
)

votes_namespace.schema_model(
    "VoteListSuccessResponse", VoteListSuccessResponse.apidoc()
)


@votes_namespace.route("")
class VoteList(Resource):
    @access_granted_only("api_vote_list_get")
    @votes_namespace.doc(
        description="Endpoint to list Vote objects in bulk",
        responses={
            200: ("Success", "VoteListSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "challenge_id": (int, None),
            "user_id": (int, None),
            "value": (bool, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "VoteFields", {"user_id": "user_id", "value": "value"}
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Votes, query=q, field=field)
        votes = Votes.query.filter_by(**query_args).filter(*filters).all()
        schema = VoteSchema(many=True)
        response = schema.dump(votes)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_vote_list_post")
    @votes_namespace.doc(
        description="Endpoint to create a Vote object",
        responses={
            200: ("Success", "VoteDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = VoteSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge = Challenges.query.filter_by(id=response.data.challenge_id).first_or_404()
        already_voted = Votes.query.filter_by(challenge_id=challenge.id, user_id=session["id"]).first()
        response.data.user_id = session["id"]
        db.session.add(response.data)

        if challenge.state == "voting" and challenge.author_id != session["id"] and already_voted is None:
            db.session.commit()

            response = schema.dump(response.data)
            db.session.close()

            return {"success": True, "data": response.data}
        return {"success": False}


@votes_namespace.route("/<vote_id>")
class Vote(Resource):
    @access_granted_only("api_vote_get")
    @votes_namespace.doc(
        description="Endpoint to get a specific Vote object",
        responses={
            200: ("Success", "VoteDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, vote_id):
        vote = Votes.query.filter_by(id=vote_id).first_or_404()

        response = VoteSchema().dump(vote)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_vote_delete")
    @votes_namespace.doc(
        description="Endpoint to delete a specific Vote object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, vote_id):
        vote = Votes.query.filter_by(id=vote_id).first_or_404()
        challenge = Challenges.query.filter_by(id=vote.challenge_id).first_or_404()
        if challenge.state == "voting" and (has_right("api_vote_delete_full") or
                                            (has_right("api_vote_delete_partial") and vote.user_id == session["id"])):
            db.session.delete(vote)
            db.session.commit()
            db.session.close()

            return {"success": True}
        return{"success": False}

    @access_granted_only("api_vote_patch")
    @votes_namespace.doc(
        description="Endpoint to edit a specific Vote object",
        responses={
            200: ("Success", "VoteDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, vote_id):
        vote = Votes.query.filter_by(id=vote_id).first_or_404()
        challenge = Challenges.query.filter_by(id=vote.challenge_id).first_or_404()
        if challenge.state == "voting" and (has_right("api_vote_patch_full") or
                                            (has_right("api_vote_patch_partial") and vote.user_id == session["id"])):
            schema = VoteSchema()
            req = request.get_json()

            response = schema.load(req, session=db.session, instance=vote, partial=True)

            if response.errors:
                return {"success": False, "errors": response.errors}, 400

            db.session.commit()

            response = schema.dump(response.data)
            db.session.close()

            return {"success": True, "data": response.data}
        return {"success": False}
