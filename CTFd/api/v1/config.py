from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.cache import clear_config
from CTFd.constants import RawEnum
from CTFd.models import Configs, Fields, db
from CTFd.schemas.config import ConfigSchema
from CTFd.schemas.fields import FieldSchema
from CTFd.utils import set_config
from CTFd.utils.decorators import access_granted_only
from CTFd.utils.helpers.models import build_model_filters

configs_namespace = Namespace("configs", description="Endpoint to retrieve Configs")

ConfigModel = sqlalchemy_to_pydantic(Configs)


class ConfigDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: ConfigModel


class ConfigListSuccessResponse(APIListSuccessResponse):
    data: List[ConfigModel]


configs_namespace.schema_model(
    "ConfigDetailedSuccessResponse", ConfigDetailedSuccessResponse.apidoc()
)

configs_namespace.schema_model(
    "ConfigListSuccessResponse", ConfigListSuccessResponse.apidoc()
)


@configs_namespace.route("")
class ConfigList(Resource):
    @access_granted_only("api_config_list_get")
    @configs_namespace.doc(
        description="Endpoint to get Config objects in bulk",
        responses={
            200: ("Success", "ConfigListSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "key": (str, None),
            "value": (str, None),
            "q": (str, None),
            "field": (RawEnum("ConfigFields", {"key": "key", "value": "value"}), None),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Configs, query=q, field=field)

        configs = Configs.query.filter_by(**query_args).filter(*filters).all()
        schema = ConfigSchema(many=True)
        response = schema.dump(configs)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_config_list_post")
    @configs_namespace.doc(
        description="Endpoint to get create a Config object",
        responses={
            200: ("Success", "ConfigDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = ConfigSchema()
        response = schema.load(req)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        clear_config()

        return {"success": True, "data": response.data}

    @access_granted_only("api_config_list_patch")
    @configs_namespace.doc(
        description="Endpoint to get patch Config objects in bulk",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def patch(self):
        req = request.get_json()

        for key, value in req.items():
            set_config(key=key, value=value)

        clear_config()

        return {"success": True}


@configs_namespace.route("/<config_key>")
class Config(Resource):
    @access_granted_only("api_config_get")
    @configs_namespace.doc(
        description="Endpoint to get a specific Config object",
        responses={
            200: ("Success", "ConfigDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, config_key):
        config = Configs.query.filter_by(key=config_key).first_or_404()
        schema = ConfigSchema()
        response = schema.dump(config)
        return {"success": True, "data": response.data}

    @access_granted_only("api_config_patch")
    @configs_namespace.doc(
        description="Endpoint to edit a specific Config object",
        responses={
            200: ("Success", "ConfigDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, config_key):
        config = Configs.query.filter_by(key=config_key).first()
        data = request.get_json()
        if config:
            schema = ConfigSchema(instance=config, partial=True)
            response = schema.load(data)
        else:
            schema = ConfigSchema()
            data["key"] = config_key
            response = schema.load(data)
            db.session.add(response.data)

        if response.errors:
            return response.errors, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        clear_config()

        return {"success": True, "data": response.data}

    @access_granted_only("api_config_delete")
    @configs_namespace.doc(
        description="Endpoint to delete a Config object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, config_key):
        config = Configs.query.filter_by(key=config_key).first_or_404()

        db.session.delete(config)
        db.session.commit()
        db.session.close()

        clear_config()

        return {"success": True}


@configs_namespace.route("/fields")
class FieldList(Resource):
    @access_granted_only("api_field_list_get")
    @validate_args(
        {
            "type": (str, None),
            "q": (str, None),
            "field": (RawEnum("FieldFields", {"description": "description"}), None),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Fields, query=q, field=field)

        fields = Fields.query.filter_by(**query_args).filter(*filters).all()
        schema = FieldSchema(many=True)

        response = schema.dump(fields)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_field_list_post")
    def post(self):
        req = request.get_json()
        schema = FieldSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@configs_namespace.route("/fields/<field_id>")
class Field(Resource):
    @access_granted_only("api_field_get")
    def get(self, field_id):
        field = Fields.query.filter_by(id=field_id).first_or_404()
        schema = FieldSchema()

        response = schema.dump(field)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @access_granted_only("api_field_patch")
    def patch(self, field_id):
        field = Fields.query.filter_by(id=field_id).first_or_404()
        schema = FieldSchema()

        req = request.get_json()

        response = schema.load(req, session=db.session, instance=field)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

    @access_granted_only("api_field_delete")
    def delete(self, field_id):
        field = Fields.query.filter_by(id=field_id).first_or_404()
        db.session.delete(field)
        db.session.commit()
        db.session.close()

        return {"success": True}
