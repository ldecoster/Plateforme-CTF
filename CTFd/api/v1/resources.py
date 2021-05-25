from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Challenges, Resources, db
from CTFd.schemas.resources import ResourceSchema
from CTFd.utils.decorators import access_granted_only, authed_only
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.user import has_right_or_is_author

resources_namespace = Namespace("resources", description="Endpoint to retrieve Resources")

ResourceModel = sqlalchemy_to_pydantic(Resources)


class ResourceDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: ResourceModel


class ResourceListSuccessResponse(APIListSuccessResponse):
    data: List[ResourceModel]


resources_namespace.schema_model(
    "ResourceDetailedSuccessResponse", ResourceDetailedSuccessResponse.apidoc()
)

resources_namespace.schema_model(
    "ResourceListSuccessResponse", ResourceListSuccessResponse.apidoc()
)


@resources_namespace.route("")
class ResourceList(Resource):
    @access_granted_only("api_resource_list_get")
    @resources_namespace.doc(
        description="Endpoint to list Resource objects in bulk",
        responses={
            200: ("Success", "ResourceListSuccessResponse"),
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
                RawEnum("ResourceFields", {"type": "type", "content": "content"}),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Resources, query=q, field=field)

        resources = Resources.query.filter_by(**query_args).filter(*filters).all()
        response = ResourceSchema(many=True, view="user").dump(resources)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @resources_namespace.doc(
        description="Endpoint to create a Resource object",
        responses={
            200: ("Success", "ResourceDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = ResourceSchema(view="admin")
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge = Challenges.query.filter_by(id=response.data.challenge_id).first_or_404()
        db.session.add(response.data)

        if has_right_or_is_author("api_resource_list_post", challenge.author_id):
            db.session.commit()

            response = schema.dump(response.data)

            return {"success": True, "data": response.data}
        return {"success": False}


@resources_namespace.route("/<resource_id>")
class Resource(Resource):
    @authed_only
    @resources_namespace.doc(
        description="Endpoint to get a specific Resource object",
        responses={
            200: ("Success", "ResourceDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, resource_id):
        resource = Resources.query.filter_by(id=resource_id).first_or_404()

        response = ResourceSchema(view="user").dump(resource)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @resources_namespace.doc(
        description="Endpoint to edit a specific Resource object",
        responses={
            200: ("Success", "ResourceDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, resource_id):
        resource = Resources.query.filter_by(id=resource_id).first_or_404()
        challenge = Challenges.query.filter_by(id=resource.challenge_id).first_or_404()
        if has_right_or_is_author("api_resource_patch", challenge.author_id):
            req = request.get_json()

            schema = ResourceSchema(view="admin")
            response = schema.load(req, instance=resource, partial=True, session=db.session)

            if response.errors:
                return {"success": False, "errors": response.errors}, 400

            db.session.add(response.data)
            db.session.commit()

            response = schema.dump(response.data)

            return {"success": True, "data": response.data}
        return {"success": False}

    @resources_namespace.doc(
        description="Endpoint to delete a specific Tag object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, resource_id):
        resource = Resources.query.filter_by(id=resource_id).first_or_404()
        challenge = Challenges.query.filter_by(id=resource.challenge_id).first_or_404()
        if has_right_or_is_author("api_resource_delete", challenge.author_id):
            db.session.delete(resource)
            db.session.commit()
            db.session.close()

            return {"success": True}
        return {"success": False}
