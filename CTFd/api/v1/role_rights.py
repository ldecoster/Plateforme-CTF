from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import db, RoleRights
from CTFd.schemas.role_rights import RoleRightsSchema
from CTFd.utils.decorators import access_granted_only
from CTFd.utils.helpers.models import build_model_filters

role_rights_namespace = Namespace("role_rights", description="Endpoint to retrieve RoleRights")

RoleRightsModel = sqlalchemy_to_pydantic(RoleRights)


class RoleRightsDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: RoleRightsModel


class RoleRightsListSuccessResponse(APIListSuccessResponse):
    data: List[RoleRightsModel]


role_rights_namespace.schema_model(
    "RoleRightsDetailedSuccessResponse", RoleRightsDetailedSuccessResponse.apidoc()
)

role_rights_namespace.schema_model("RoleRightsListSuccessResponse", RoleRightsListSuccessResponse.apidoc())


@role_rights_namespace.route("")
class RoleRightsList(Resource):
    @access_granted_only("api_role_rights_list_get")
    @role_rights_namespace.doc(
        description="Endpoint to list RoleRights objects in bulk",
        responses={
            200: ("Success", "RoleRightsListSuccessResponse"),
            400: (
                    "An error occurred processing the provided or stored data",
                    "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "role_id": (int, None),
            "right_id": (int, None),
            "q": (str, None),
            "field": (
                    RawEnum(
                        "RoleRightsFields",
                        {
                            "role_id": "role_id",
                            "right_id": "right_id"
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
        filters = build_model_filters(model=RoleRights, query=q, field=field)

        role_rights = RoleRights.query.filter_by(**query_args).filter(*filters).all()
        schema = RoleRightsSchema(many=True)
        response = schema.dump(role_rights)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_role_rights_list_post")
    @role_rights_namespace.doc(
        description="Endpoint to create a RoleRights object",
        responses={
            200: ("Success", "RoleRightsDetailedSuccessResponse"),
            400: (
                    "An error occurred processing the provided or stored data",
                    "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = RoleRightsSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@role_rights_namespace.route("/<role_id>/<right_id>")
@role_rights_namespace.param("role_id", "A Role ID")
@role_rights_namespace.param("right_id", "A Right ID")
class RoleRights(Resource):
    @access_granted_only("api_role_rights_get")
    @role_rights_namespace.doc(
        description="Endpoint to get a specific RoleRights object",
        responses={
            200: ("Success", "RoleRightsDetailedSuccessResponse"),
            400: (
                    "An error occurred processing the provided or stored data",
                    "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, role_id, right_id):
        role_rights = RoleRights.query.filter_by(role_id=role_id, right_id=right_id).first_or_404()

        response = RoleRightsSchema().dump(role_rights)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_role_rights_delete")
    @role_rights_namespace.doc(
        description="Endpoint to delete a specific RoleRights object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, role_id, right_id):
        role_rights = RoleRights.query.filter_by(role_id=role_id, right_id=right_id).first_or_404()
        db.session.delete(role_rights)
        db.session.commit()
        db.session.close()

        return {"success": True}
