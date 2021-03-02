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
    Solves,
    Submissions,
    Tags,
    db, Fails,
)
from CTFd.plugins.badges import BADGE_CLASSES, get_badge_class
from CTFd.schemas.flags import FlagSchema
from CTFd.schemas.hints import HintSchema
from CTFd.schemas.tags import TagSchema
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
from CTFd.utils.decorators.visibility import (
    check_badge_visibility,
    check_score_visibility,
)
from CTFd.utils.helpers.models import build_model_filters
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
    @check_badge_visibility
    @during_ctf_time_only
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
        # Build filtering queries
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Badges, query=q, field=field)

        # This can return None (unauth) if visibility is set to public
        user = get_current_user()

        # Admins can request to see everything
        if is_admin() and request.args.get("view") == "admin":
            badges = (
                Badges.query.filter_by(**query_args)
                .filter(*filters)
                .all()
            )
            solve_ids = set([badge.id for badge in badges])
        else:
            badges = (
                Badges.query.filter(
                    and_(Badges.state != "hidden", Badges.state != "locked", Badges.state != "voting")
                )
                .filter_by(**query_args)
                .filter(*filters)
                .all()
            )

            if user:
                solve_ids = (
                    Solves.query.with_entities(Solves.badge_id)
                    .filter_by(account_id=user.account_id)
                    .order_by(Solves.badge_id.asc())
                    .all()
                )
                solve_ids = set([value for value, in solve_ids])

                # TODO: Convert this into a re-useable decorator
                if is_admin():
                    pass
            else:
                solve_ids = set()

        response = []
        tag_schema = TagSchema(view="user", many=True)
        for badge in badges:
            if badge.requirements:
                requirements = badge.requirements.get("prerequisites", [])
                anonymize = badge.requirements.get("anonymize")
                prereqs = set(requirements)
                if solve_ids >= prereqs:
                    pass
                else:
                    if anonymize:
                        response.append(
                            {
                                "id": badge.id,
                                "type": "hidden",
                                "name": "???",
                                "value": 0,
                                "tags": [],
                                "template": "",
                                "script": "",
                            }
                        )
                    # Fallthrough to continue
                    continue

            try:
                badge_type = get_badge_class(badge.type)
            except KeyError:
                # Badge type does not exist. Fall through to next badge.
                continue

            # Badge passes all checks, add it to response
            # TODO ISEN : remove unused "value" and "category"
            response.append(
                {
                    "id": badge.id,
                    "type": badge_type.name,
                    "name": badge.name,
                    "value": 0,
                    "tags": tag_schema.dump(badge.tags).data,
                    "template": badge_type.templates["view"],
                    "script": badge_type.scripts["view"],
                }
            )

        db.session.close()
        return {"success": True, "data": response}

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
        data = request.form or request.get_json()
        badge_type = data["type"]
        data["author_id"] = session["id"]
        badge_class = get_badge_class(badge_type)
        badge = badge_class.create(request)
        response = badge_class.read(badge)
        return {"success": True, "data": response}


@badges_namespace.route("/types")
class BadgeTypes(Resource):
    @contributors_teachers_admins_only
    def get(self):
        response = {}

        for class_id in BADGE_CLASSES:
            badge_class = BADGE_CLASSES.get(class_id)
            response[badge_class.id] = {
                "id": badge_class.id,
                "name": badge_class.name,
                "templates": badge_class.templates,
                "scripts": badge_class.scripts,
                "create": render_template(
                    badge_class.templates["create"].lstrip("/")
                ),
            }
        return {"success": True, "data": response}


@badges_namespace.route("/<badge_id>")
class Badge(Resource):
    @check_badge_visibility
    @during_ctf_time_only
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

        if badge.requirements:
            requirements = badge.requirements.get("prerequisites", [])
            anonymize = badge.requirements.get("anonymize")
            if badges_visible():
                user = get_current_user()
                if user:
                    solve_ids = (
                        Solves.query.with_entities(Solves.badge_id)
                            .filter_by(account_id=user.account_id)
                            .order_by(Solves.badge_id.asc())
                            .all()
                    )
                else:
                    # We need to handle the case where a user is viewing badges anonymously
                    solve_ids = []
                solve_ids = set([value for value, in solve_ids])
                prereqs = set(requirements)
                if solve_ids >= prereqs or is_admin():
                    pass
                else:
                    if anonymize:
                        return {
                            "success": True,
                            "data": {
                                "id": badge.id,
                                "type": "hidden",
                                "name": "???",
                                "value": 0,
                                "tags": [],
                                "template": "",
                                "script": "",
                            },
                        }
                    abort(403)
            else:
                abort(403)

        tags = [
            tag["value"] for tag in TagSchema("user", many=True).dump(badge.tags).data
        ]

        response = badge_class.read(badge=badge)

        Model = get_model()

        if scores_visible() is True and accounts_visible() is True:
            solves = Solves.query.join(Model, Solves.account_id == Model.id).filter(
                Solves.badge_id == badge.id,
                Model.banned == False,
                Model.hidden == False,
                )

            # Only show solves that happened before freeze time if configured
            freeze = get_config("freeze")
            if not is_admin() and freeze:
                solves = solves.filter(Solves.date < unix_time_to_utc(freeze))

            solves = solves.count()
            response["solves"] = solves
        else:
            response["solves"] = None
            solves = None

        if authed():
            # Get current attempts for the user
            attempts = Submissions.query.filter_by(
                account_id=user.account_id, badge_id=badge_id
            ).count()
        else:
            attempts = 0

        response["attempts"] = attempts
        response["files"] = files
        response["tags"] = tags
        response["hints"] = hints

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


@badges_namespace.route("/attempt")
class BadgeAttempt(Resource):
    @check_badge_visibility
    @during_ctf_time_only
    @require_verified_emails
    def post(self):
        if authed() is False:
            return {"success": True, "data": {"status": "authentication_required"}}, 403

        if request.content_type != "application/json":
            request_data = request.form
        else:
            request_data = request.get_json()

        badge_id = request_data.get("badge_id")

        if current_user.is_admin():
            preview = request.args.get("preview", False)
            if preview:
                badge = Badges.query.filter_by(id=badge_id).first_or_404()
                badge_class = get_badge_class(badge.type)
                status, message = badge_class.attempt(badge, request)

                return {
                    "success": True,
                    "data": {
                        "status": "correct" if status else "incorrect",
                        "message": message,
                    },
                }

        if ctf_paused():
            return (
                {
                    "success": True,
                    "data": {
                        "status": "paused",
                        "message": "{} is paused".format(config.ctf_name()),
                    },
                },
                403,
            )

        user = get_current_user()

        fails = Fails.query.filter_by(
            account_id=user.account_id, badge_id=badge_id
        ).count()

        badge = Badges.query.filter_by(id=badge_id).first_or_404()

        if badge.state == "hidden":
            abort(404)

        if badge.state == "locked":
            abort(403)

        if badge.requirements:
            requirements = badge.requirements.get("prerequisites", [])
            solve_ids = (
                Solves.query.with_entities(Solves.badge_id)
                .filter_by(account_id=user.account_id)
                .order_by(Solves.badge_id.asc())
                .all()
            )
            solve_ids = set([solve_id for solve_id, in solve_ids])
            prereqs = set(requirements)
            if solve_ids >= prereqs:
                pass
            else:
                abort(403)

        badge_class = get_badge_class(badge.type)

        # Anti-bruteforce / submitting Flags too quickly
        kpm = current_user.get_wrong_submissions_per_minute(user.account_id)
        if kpm > 10:
            if ctftime():
                badge_class.fail(
                    user=user, badge=badge, request=request
                )
            log(
                "submissions",
                "[{date}] {name} submitted {submission} on {badge_id} with kpm {kpm} [TOO FAST]",
                submission=request_data.get("submission", "").encode("utf-8"),
                badge_id=badge_id,
                kpm=kpm,
            )
            # Submitting too fast
            return (
                {
                    "success": True,
                    "data": {
                        "status": "ratelimited",
                        "message": "You're submitting flags too fast. Slow down.",
                    },
                },
                429,
            )

        solves = Solves.query.filter_by(
            account_id=user.account_id, badge_id=badge_id
        ).first()

        # badge not solved yet
        if not solves:
            # Hit max attempts
            max_tries = badge.max_attempts
            if max_tries and fails >= max_tries > 0:
                return (
                    {
                        "success": True,
                        "data": {
                            "status": "incorrect",
                            "message": "You have 0 tries remaining",
                        },
                    },
                    403,
                )

            status, message = badge_class.attempt(badge, request)
            if status:  # The badge plugin says the input is right
                if ctftime() or current_user.is_admin():
                    badge_class.solve(
                        user=user, badge=badge, request=request
                    )
                    clear_standings()

                log(
                    "submissions",
                    "[{date}] {name} submitted {submission} on {badge_id} with kpm {kpm} [CORRECT]",
                    submission=request_data.get("submission", "").encode("utf-8"),
                    badge_id=badge_id,
                    kpm=kpm,
                )
                return {
                    "success": True,
                    "data": {"status": "correct", "message": message},
                }
            else:  # The badge plugin says the input is wrong
                if ctftime() or current_user.is_admin():
                    badge_class.fail(
                        user=user, badge=badge, request=request
                    )
                    clear_standings()

                log(
                    "submissions",
                    "[{date}] {name} submitted {submission} on {badge_id} with kpm {kpm} [WRONG]",
                    submission=request_data.get("submission", "").encode("utf-8"),
                    badge_id=badge_id,
                    kpm=kpm,
                )

                if max_tries:
                    # Off by one since fails has changed since it was gotten
                    attempts_left = max_tries - fails - 1
                    tries_str = "tries"
                    if attempts_left == 1:
                        tries_str = "try"
                    # Add a punctuation mark if there isn't one
                    if message[-1] not in "!().;?[]{}":
                        message = message + "."
                    return {
                        "success": True,
                        "data": {
                            "status": "incorrect",
                            "message": "{} You have {} {} remaining.".format(
                                message, attempts_left, tries_str
                            ),
                        },
                    }
                else:
                    return {
                        "success": True,
                        "data": {"status": "incorrect", "message": message},
                    }

        # badge already solved
        else:
            log(
                "submissions",
                "[{date}] {name} submitted {submission} on {badge_id} with kpm {kpm} [ALREADY SOLVED]",
                submission=request_data.get("submission", "").encode("utf-8"),
                badge_id=badge_id,
                kpm=kpm,
            )
            return {
                "success": True,
                "data": {
                    "status": "already_solved",
                    "message": "You already solved this",
                },
            }




