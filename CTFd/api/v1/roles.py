from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Roles, db
from CTFd.schemas.roles import RoleSchema
from CTFd.utils.decorators import access_granted_only
from CTFd.utils.helpers.models import build_model_filters

roles_namespace = Namespace("roles", description="Endpoint to retrieve Roles")

RoleModel = sqlalchemy_to_pydantic(Roles)


class RoleDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: RoleModel


class RoleListSuccessResponse(APIListSuccessResponse):
    data: List[RoleModel]


roles_namespace.schema_model(
    "RoleDetailedSuccessResponse", RoleDetailedSuccessResponse.apidoc()
)

roles_namespace.schema_model(
    "RoleListSuccessResponse", RoleListSuccessResponse.apidoc()
)


@roles_namespace.route("")
class RoleList(Resource):
    @access_granted_only("api_role_list_get")
    @roles_namespace.doc(
        description="Endpoint to list Role objects in bulk",
        responses={
            200: ("Success", "RoleListSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "name": (str, None),
            "q": (str, None),
            "field": (RawEnum("RoleFields", {"name": "name"}), None),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Roles, query=q, field=field)

        roles = Roles.query.filter_by(**query_args).filter(*filters).all()
        schema = RoleSchema(many=True)
        response = schema.dump(roles)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_role_list_post")
    @roles_namespace.doc(
        description="Endpoint to create a Role object",
        responses={
            200: ("Success", "RoleListSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = RoleSchema()

        response = schema.load(req, session=db.session)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@roles_namespace.route("/<role_id>")
@roles_namespace.param("role_id", "A Role ID")
class Role(Resource):
    @access_granted_only("api_role_get")
    @roles_namespace.doc(
        description="Endpoint to get a specific Role object",
        responses={
            200: ("Success", "RoleDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, role_id):
        role = Roles.query.filter_by(id=role_id).first_or_404()
        response = RoleSchema().dump(role)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_role_delete")
    @roles_namespace.doc(
        description="Endpoint to delete a Role object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, role_id):
        role = Roles.query.filter_by(id=role_id).first_or_404()
        db.session.delete(role)
        db.session.commit()
        db.session.close()

        return {"success": True}
