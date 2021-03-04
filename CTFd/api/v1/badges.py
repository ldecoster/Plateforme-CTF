import datetime
from typing import List

from flask import abort, render_template, request, url_for
from flask_restx import Namespace, Resource
from sqlalchemy.sql import and_

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import (
    Badges,
    db, Fails,
)
from CTFd.schemas.badges import BadgeSchema
from CTFd.utils import config, get_config
from CTFd.utils import sessions
from CTFd.utils import user as current_user
from CTFd.utils.config import get_votes_number
from CTFd.utils.config.visibility import (
    accounts_visible,
    badges_visible,

)
from CTFd.utils.dates import  ctf_paused, isoformat, unix_time_to_utc
from CTFd.utils.decorators import (
    admins_only,
    contributors_teachers_admins_only,
    teachers_admins_only,
    require_verified_emails,
)


from CTFd.utils.logging import log
from CTFd.utils.modes import generate_account_url, get_model
from CTFd.utils.security.signing import serialize
from CTFd.utils.user import authed, get_current_user, is_admin, is_contributor, is_teacher
from CTFd.utils.security.auth import login_user
from flask import session

badges_namespace = Namespace(
    "badges", description="Endpoint to retrieve badges"
)

BadgeModel = sqlalchemy_to_pydantic(Badges)
TransientBadgeModel = sqlalchemy_to_pydantic(Badges, exclude=["id"])


class BadgeDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: BadgeModel


class BadgeListSuccessResponse(APIListSuccessResponse):
    data: List[BadgeModel]


badges_namespace.schema_model(
    "badgeDetailedSuccessResponse", BadgeDetailedSuccessResponse.apidoc()
)

badges_namespace.schema_model(
    "badgeListSuccessResponse", BadgeListSuccessResponse.apidoc()
)


@badges_namespace.route("")
class BadgeList(Resource):
    @require_verified_emails
    @badges_namespace.doc(
        description="Endpoint to get badge objects in bulk",
        responses={
            200: ("Success", "badgeListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "name": (str, None),
            "max_attempts": (int, None),
            "value": (int, None),
            "type": (str, None),
            "state": (str, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "BadgeFields",
                    {
                        "name": "name",
                        "description": "description",
                        "type": "type",
                        "state": "state",
                    },
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Badges, query=q, field=field)

        badges = Badges.query.filter_by(**query_args).filter(*filters).all()
        schema = BadgeSchema(many=True)
        response = schema.dump(badges)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @contributors_teachers_admins_only
    @badges_namespace.doc(
        description="Endpoint to create a badge object",
        responses={
            200: ("Success", "BadgeDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = BadgeSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)

        if is_admin() or is_teacher() or is_contributor():
            db.session.commit()

            response = schema.dump(response.data)
            db.session.close()

            return {"success": True, "data": response.data}
        return {"success": False}


@badges_namespace.route("/<badge_id>")
class Badge(Resource):
    @require_verified_emails
    @badges_namespace.doc(
        description="Endpoint to get a specific badge object",
        responses={
            200: ("Success", "badgeDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, badge_id):
        if is_admin():
            badge = Badges.query.filter(Badges.id == badge_id).first_or_404()
        else:
            badge = Badges.query.filter(
                Badges.id == badge_id,
                and_(Badges.state != "hidden", Badges.state != "locked"),
                ).first_or_404()

        try:
            badge_class = get_badge_class(badge.type)
        except KeyError:
            abort(
                500,
                f"The underlying badge type ({badge.type}) is not installed. This badge can not be loaded.",
            )

        response = badge_class.read(badge=badge)

        Model = get_model()

        response["view"] = render_template(
            badge_class.templates["view"].lstrip("/"),
            solves=solves,
            files=files,
            tags=tags,
            badge=badge,
        )

        db.session.close()
        return {"success": True, "data": response}

    @contributors_teachers_admins_only
    @badges_namespace.doc(
        description="Endpoint to edit a specific badge object",
        responses={
            200: ("Success", "badgeDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, badge_id):
        author_id = session["id"]
        badge = Badges.query.filter_by(id=badge_id).first_or_404()
        data = request.form or request.get_json()
        badge_new_state = None

        # Check state's value to avoid unwanted input from the user
        if 'state' in data:
            badge_new_state = data['state']
            if badge_new_state != "visible" and badge_new_state != "voting" and badge_new_state != "hidden":
                return {"success": False}

        if is_admin() or is_teacher():
            badge_class = get_badge_class(badge.type)
            badge = badge_class.update(badge, request)
            response = badge_class.read(badge)
            return {"success": True, "data": response}
        elif is_contributor() and badge.author_id == author_id:
            badge_class = get_badge_class(badge.type)

            # Check the number of votes before changing the state of the badge
            if badge_new_state == "visible" and badge.state == "voting":
                positive_votes = Votes.query.filter_by(badge_id=badge.id, value=1).count()
                negative_votes = Votes.query.filter_by(badge_id=badge.id, value=0).count()
                votes_delta = get_votes_number()
                # If positives votes minus the delta is not greater than or equal to the negative votes, abort
                if (positive_votes - votes_delta) < negative_votes:
                    return {"success": False, "errors": "votes"}

            badge = badge_class.update(badge, request)
            response = badge_class.read(badge)
            return {"success": True, "data": response}
        return {"success": False}

    @contributors_teachers_admins_only
    @badges_namespace.doc(
        description="Endpoint to delete a specific badge object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, badge_id):
        author_id = session["id"]
        badge = Badges.query.filter_by(id=badge_id).first_or_404()
        if is_admin() or is_teacher() or (is_contributor() and badge.author_id==author_id):
            badge_class = get_badge_class(badge.type)
            badge_class.delete(badge)

            return {"success": True}
        return {"success": False}

