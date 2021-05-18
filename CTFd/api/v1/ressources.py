from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Challenges, Ressources, db
from CTFd.schemas.ressources import RessourceSchema
from CTFd.utils.decorators import access_granted_only, authed_only
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.user import has_right_or_is_author

ressources_namespace = Namespace("ressources", description="Endpoint to retrieve Ressources")

RessourceModel = sqlalchemy_to_pydantic(Ressources)


class RessourceDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: RessourceModel


class RessourceListSuccessResponse(APIListSuccessResponse):
    data: List[RessourceModel]


ressources_namespace.schema_model(
    "RessourceDetailedSuccessResponse", RessourceDetailedSuccessResponse.apidoc()
)

ressources_namespace.schema_model(
    "RessourceListSuccessResponse", RessourceListSuccessResponse.apidoc()
)


@ressources_namespace.route("")
class RessourceList(Resource):
    @access_granted_only("api_ressource_list_get")
    @ressources_namespace.doc(
        description="Endpoint to list Ressource objects in bulk",
        responses={
            200: ("Success", "RessourceListSuccessResponse"),
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
                RawEnum("RessourceFields", {"type": "type", "content": "content"}),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Ressources, query=q, field=field)

        ressources = Ressources.query.filter_by(**query_args).filter(*filters).all()
        response = RessourceSchema(many=True).dump(ressources)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_ressource_list_post")
    @ressources_namespace.doc(
        description="Endpoint to create a Ressource object",
        responses={
            200: ("Success", "RessourceDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = RessourceSchema(view="admin")
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge = Challenges.query.filter_by(id=response.data.challenge_id).first_or_404()
        db.session.add(response.data)

        if has_right_or_is_author("api_ressource_list_post", challenge.author_id):
            db.session.commit()

            response = schema.dump(response.data)

            return {"success": True, "data": response.data}
        return {"success": False}


@ressources_namespace.route("/<ressource_id>")
class Ressource(Resource):
    @authed_only
    @ressources_namespace.doc(
        description="Endpoint to get a specific Ressource object",
        responses={
            200: ("Success", "RessourceDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, ressource_id):
        ressource = Ressources.query.filter_by(id=ressource_id).first_or_404()

        response = RessourceSchema().dump(ressource)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_ressource_patch")
    @ressources_namespace.doc(
        description="Endpoint to edit a specific Ressource object",
        responses={
            200: ("Success", "RessourceDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, ressource_id):
        ressource = Ressources.query.filter_by(id=ressource_id).first_or_404()
        challenge = Challenges.query.filter_by(id=ressource.challenge_id).first_or_404()
        if has_right_or_is_author("api_ressource_patch", challenge.author_id):
            req = request.get_json()

            schema = RessourceSchema(view="admin")
            response = schema.load(req, instance=ressource, partial=True, session=db.session)

            if response.errors:
                return {"success": False, "errors": response.errors}, 400

            db.session.add(response.data)
            db.session.commit()

            response = schema.dump(response.data)

            return {"success": True, "data": response.data}
        return {"success": False}

    @access_granted_only("api_ressource_delete")
    @ressources_namespace.doc(
        description="Endpoint to delete a specific Tag object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, ressource_id):
        ressource = Ressources.query.filter_by(id=ressource_id).first_or_404()
        challenge = Challenges.query.filter_by(id=ressource.challenge_id).first_or_404()
        if has_right_or_is_author("api_ressource_delete", challenge.author_id):
            db.session.delete(ressource)
            db.session.commit()
            db.session.close()

            return {"success": True}
        return {"success": False}
