from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import db, UserRights
from CTFd.schemas.user_rights import UserRightsSchema
from CTFd.utils.decorators import contributors_teachers_admins_only
from CTFd.utils.helpers.models import build_model_filters

user_rights_namespace = Namespace("user_rights", description="Endpoint to retrieve UserRights")

UserRightsModel = sqlalchemy_to_pydantic(UserRights)


class UserRightsDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: UserRightsModel


class UserRightsListSuccessResponse(APIListSuccessResponse):
    data: List[UserRightsModel]


user_rights_namespace.schema_model(
    "UserRightsDetailedSuccessResponse", UserRightsDetailedSuccessResponse.apidoc()
)

user_rights_namespace.schema_model("UserRightsListSuccessResponse", UserRightsListSuccessResponse.apidoc())


@user_rights_namespace.route("")
class UserRightsList(Resource):
    @contributors_teachers_admins_only
    @user_rights_namespace.doc(
        description="Endpoint to list UserRights objects in bulk",
        responses={
            200: ("Success", "UserRightsListSuccessResponse"),
            400: (
                    "An error occurred processing the provided or stored data",
                    "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "user_id": (int, None),
            "right_id": (int, None),
            "q": (str, None),
            "field": (
                    RawEnum(
                        "UserRightsFields",
                        {
                            "user_id": "user_id",
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
        filters = build_model_filters(model=UserRights, query=q, field=field)

        user_rights = UserRights.query.filter_by(**query_args).filter(*filters).all()
        schema = UserRightsSchema(many=True)
        response = schema.dump(user_rights)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @contributors_teachers_admins_only
    @user_rights_namespace.doc(
        description="Endpoint to create a UserRights object",
        responses={
            200: ("Success", "UserRightsDetailedSuccessResponse"),
            400: (
                    "An error occurred processing the provided or stored data",
                    "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = UserRightsSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@user_rights_namespace.route("/<user_id>/<right_id>")
@user_rights_namespace.param("user_id", "A User ID")
@user_rights_namespace.param("right_id", "A Right ID")
class UserRights(Resource):
    @contributors_teachers_admins_only
    @user_rights_namespace.doc(
        description="Endpoint to get a specific UserRights object",
        responses={
            200: ("Success", "UserRightsDetailedSuccessResponse"),
            400: (
                    "An error occurred processing the provided or stored data",
                    "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, user_id, right_id):
        user_rights = UserRights.query.filter_by(user_id=user_id, right_id=right_id).first_or_404()

        response = UserRightsSchema().dump(user_rights)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @contributors_teachers_admins_only
    @user_rights_namespace.doc(
        description="Endpoint to delete a specific UserRights object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, user_id, right_id):
        user_rights = UserRights.query.filter_by(user_id=user_id, right_id=right_id).first_or_404()
        db.session.delete(user_rights)
        db.session.commit()
        db.session.close()

        return {"success": True}
