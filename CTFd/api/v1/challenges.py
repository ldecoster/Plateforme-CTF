from typing import List

from flask import abort, render_template, request, url_for
from flask_restx import Namespace, Resource
from sqlalchemy.sql import and_

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import ChallengeFiles as ChallengeFilesModel, Votes
from CTFd.models import (
    Challenges,
    Fails,
    Flags,
    Hints,
    HintUnlocks,
    Solves,
    Submissions,
    Tags,
    TagChallenge,
    db,
)
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.schemas.flags import FlagSchema
from CTFd.schemas.hints import HintSchema
from CTFd.schemas.votes import VoteSchema
from CTFd.schemas.tags import TagSchema
from CTFd.utils import config
from CTFd.utils import user as current_user
from CTFd.utils.config import get_votes_number
from CTFd.utils.config.visibility import (
    accounts_visible,
    challenges_visible,
)
from CTFd.utils.dates import ctf_paused, isoformat
from CTFd.utils.decorators import (
    contributors_teachers_admins_only,
    require_verified_emails,
)
from CTFd.utils.decorators.visibility import check_challenge_visibility
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.logging import log
from CTFd.utils.modes import generate_account_url, get_model
from CTFd.utils.security.signing import serialize
from CTFd.utils.user import authed, get_current_user, is_admin, is_contributor, is_teacher
from flask import session

challenges_namespace = Namespace(
    "challenges", description="Endpoint to retrieve Challenges"
)

ChallengeModel = sqlalchemy_to_pydantic(Challenges)
TransientChallengeModel = sqlalchemy_to_pydantic(Challenges, exclude=["id"])


class ChallengeDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: ChallengeModel


class ChallengeListSuccessResponse(APIListSuccessResponse):
    data: List[ChallengeModel]


challenges_namespace.schema_model(
    "ChallengeDetailedSuccessResponse", ChallengeDetailedSuccessResponse.apidoc()
)

challenges_namespace.schema_model(
    "ChallengeListSuccessResponse", ChallengeListSuccessResponse.apidoc()
)


@challenges_namespace.route("")
class ChallengeList(Resource):
    @check_challenge_visibility
    @require_verified_emails
    @challenges_namespace.doc(
        description="Endpoint to get Challenge objects in bulk",
        responses={
            200: ("Success", "ChallengeListSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
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
            "author_id":(str,None),
            "field": (
                RawEnum(
                    "ChallengeFields",
                    {
                        "name": "name",
                        "description": "description",
                        "type": "type",
                        "state": "state",
                        "author_id":"author_id",
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
        filters = build_model_filters(model=Challenges, query=q, field=field)

        # This can return None (unauth) if visibility is set to public
        user = get_current_user()

        # Admins can request to see everything
        if is_admin() and request.args.get("view") == "admin":
            challenges = (
                Challenges.query.filter_by(**query_args)
                .filter(*filters)
                .all()
            )
            solve_ids = set([challenge.id for challenge in challenges])
        else:
            challenges = (
                Challenges.query.filter(
                    and_(Challenges.state != "hidden", Challenges.state != "locked", Challenges.state != "voting")
                )
                .filter_by(**query_args)
                .filter(*filters)
                .all()
            )

            if user:
                solve_ids = (
                    Solves.query.with_entities(Solves.challenge_id)
                    .filter_by(account_id=user.account_id)
                    .order_by(Solves.challenge_id.asc())
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
        for challenge in challenges:
            if challenge.requirements:
                requirements = challenge.requirements.get("prerequisites", [])
                anonymize = challenge.requirements.get("anonymize")
                prereqs = set(requirements)
                if solve_ids >= prereqs:
                    pass
                else:
                    if anonymize:
                        response.append(
                            {
                                "id": challenge.id,
                                "type": "hidden",
                                "name": "???",
                                "tags": [],
                                "authorId": "",
                                "template": "",
                                "script": "",
                            }
                        )
                    # Fallthrough to continue
                    continue

            try:
                challenge_type = get_chal_class(challenge.type)
            except KeyError:
                # Challenge type does not exist. Fall through to next challenge.
                continue

            # Challenge passes all checks, add it to response
            response.append(
                {
                    "id": challenge.id,
                    "type": challenge_type.name,
                    "name": challenge.name,
                    "tags": tag_schema.dump(challenge.tags).data,
                    "authorId": challenge.author_id,
                    "template": challenge_type.templates["view"],
                    "script": challenge_type.scripts["view"],
                }
            )

        db.session.close()
        return {"success": True, "data": response}

    @contributors_teachers_admins_only
    @challenges_namespace.doc(
        description="Endpoint to create a Challenge object",
        responses={
            200: ("Success", "ChallengeDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        data = request.form or request.get_json()
        challenge_type = data["type"]
        data["author_id"] = session["id"]
        challenge_class = get_chal_class(challenge_type)
        challenge = challenge_class.create(request)
        response = challenge_class.read(challenge)
        return {"success": True, "data": response}


@challenges_namespace.route("/types")
class ChallengeTypes(Resource):
    @contributors_teachers_admins_only
    def get(self):
        response = {}

        for class_id in CHALLENGE_CLASSES:
            challenge_class = CHALLENGE_CLASSES.get(class_id)
            response[challenge_class.id] = {
                "id": challenge_class.id,
                "name": challenge_class.name,
                "templates": challenge_class.templates,
                "scripts": challenge_class.scripts,
                "create": render_template(
                    challenge_class.templates["create"].lstrip("/")
                ),
            }
        return {"success": True, "data": response}


@challenges_namespace.route("/<challenge_id>")
class Challenge(Resource):
    @check_challenge_visibility
    @require_verified_emails
    @challenges_namespace.doc(
        description="Endpoint to get a specific Challenge object",
        responses={
            200: ("Success", "ChallengeDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, challenge_id):
        if is_admin():
            chal = Challenges.query.filter(Challenges.id == challenge_id).first_or_404()
        else:
            chal = Challenges.query.filter(
                Challenges.id == challenge_id,
                and_(Challenges.state != "hidden", Challenges.state != "locked"),
            ).first_or_404()

        try:
            chal_class = get_chal_class(chal.type)
        except KeyError:
            abort(
                500,
                f"The underlying challenge type ({chal.type}) is not installed. This challenge can not be loaded.",
            )

        if chal.requirements:
            requirements = chal.requirements.get("prerequisites", [])
            anonymize = chal.requirements.get("anonymize")
            if challenges_visible():
                user = get_current_user()
                if user:
                    solve_ids = (
                        Solves.query.with_entities(Solves.challenge_id)
                        .filter_by(account_id=user.account_id)
                        .order_by(Solves.challenge_id.asc())
                        .all()
                    )
                else:
                    # We need to handle the case where a user is viewing challenges anonymously
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
                                "id": chal.id,
                                "type": "hidden",
                                "name": "???",
                                "tags": [],
                                "authorId": "",
                                "template": "",
                                "script": "",
                            },
                        }
                    abort(403)
            else:
                abort(403)

        tags = [
            tag["value"] for tag in TagSchema("user", many=True).dump(chal.tags).data
        ]

        unlocked_hints = set()
        hints = []
        if authed():
            user = get_current_user()

            # TODO: Convert this into a re-useable decorator
            if is_admin():
                pass

            unlocked_hints = set(
                [
                    u.target
                    for u in HintUnlocks.query.filter_by(
                        type="hints", account_id=user.account_id
                    )
                ]
            )
            files = []
            for f in chal.files:
                token = {
                    "user_id": user.id,
                    "file_id": f.id,
                }
                files.append(
                    url_for("views.files", path=f.location, token=serialize(token))
                )
        else:
            files = [url_for("views.files", path=f.location) for f in chal.files]

        for hint in Hints.query.filter_by(challenge_id=chal.id).all():
            if hint.id in unlocked_hints:
                hints.append(
                    {"id": hint.id, "content": hint.content}
                )
            else:
                hints.append({"id": hint.id})

        response = chal_class.read(challenge=chal)

        Model = get_model()

        if accounts_visible() is True:
            solves = Solves.query.join(Model, Solves.account_id == Model.id).filter(
                Solves.challenge_id == chal.id,
                Model.banned == False,
                Model.hidden == False,
            )

            solves = solves.count()
            response["solves"] = solves
        else:
            response["solves"] = None
            solves = None

        if authed():
            # Get current attempts for the user
            attempts = Submissions.query.filter_by(
                account_id=user.account_id, challenge_id=challenge_id
            ).count()
        else:
            attempts = 0

        response["attempts"] = attempts
        response["files"] = files
        response["tags"] = tags
        response["hints"] = hints

        response["view"] = render_template(
            chal_class.templates["view"].lstrip("/"),
            solves=solves,
            files=files,
            tags=tags,
            hints=[Hints(**h) for h in hints],
            max_attempts=chal.max_attempts,
            attempts=attempts,
            challenge=chal,
        )

        db.session.close()
        return {"success": True, "data": response}

    @contributors_teachers_admins_only
    @challenges_namespace.doc(
        description="Endpoint to edit a specific Challenge object",
        responses={
            200: ("Success", "ChallengeDetailedSuccessResponse"),
            400: (
                "An error occurred processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, challenge_id):
        author_id = session["id"]
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        data = request.form or request.get_json()
        challenge_new_state = None

        # Check state's value to avoid unwanted input from the user
        if 'state' in data:
            challenge_new_state = data['state']
            if challenge_new_state != "visible" and challenge_new_state != "voting" and challenge_new_state != "hidden":
                return {"success": False}

        if is_admin() or is_teacher():
            challenge_class = get_chal_class(challenge.type)
            challenge = challenge_class.update(challenge, request)
            response = challenge_class.read(challenge)
            return {"success": True, "data": response}
        elif is_contributor() and challenge.author_id == author_id:
            challenge_class = get_chal_class(challenge.type)

            # Check the number of votes before changing the state of the challenge
            if challenge_new_state == "visible" and (challenge.state == "voting" or challenge.state == 'hidden'):
                positive_votes = Votes.query.filter_by(challenge_id=challenge.id, value=1).count()
                negative_votes = Votes.query.filter_by(challenge_id=challenge.id, value=0).count()
                votes_delta = get_votes_number()
                # If positives votes minus the delta is not greater than or equal to the negative votes, abort
                if (positive_votes - votes_delta) < negative_votes:
                    return {"success": False, "errors": "votes"}

            challenge = challenge_class.update(challenge, request)
            response = challenge_class.read(challenge)
            return {"success": True, "data": response}
        return {"success": False}

    @contributors_teachers_admins_only
    @challenges_namespace.doc(
        description="Endpoint to delete a specific Challenge object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, challenge_id):
        author_id = session["id"]
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        if is_admin() or is_teacher() or (is_contributor() and challenge.author_id==author_id):
            chal_class = get_chal_class(challenge.type)
            chal_class.delete(challenge)

            return {"success": True}
        return {"success": False}


@challenges_namespace.route("/attempt")
class ChallengeAttempt(Resource):
    @check_challenge_visibility
    @require_verified_emails
    def post(self):
        if authed() is False:
            return {"success": True, "data": {"status": "authentication_required"}}, 403

        if request.content_type != "application/json":
            request_data = request.form
        else:
            request_data = request.get_json()

        challenge_id = request_data.get("challenge_id")

        if current_user.is_admin():
            preview = request.args.get("preview", False)
            if preview:
                challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
                chal_class = get_chal_class(challenge.type)
                status, message = chal_class.attempt(challenge, request)

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
            account_id=user.account_id, challenge_id=challenge_id
        ).count()

        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()

        if challenge.state == "hidden":
            abort(404)

        if challenge.state == "locked":
            abort(403)

        if challenge.requirements:
            requirements = challenge.requirements.get("prerequisites", [])
            solve_ids = (
                Solves.query.with_entities(Solves.challenge_id)
                .filter_by(account_id=user.account_id)
                .order_by(Solves.challenge_id.asc())
                .all()
            )
            solve_ids = set([solve_id for solve_id, in solve_ids])
            prereqs = set(requirements)
            if solve_ids >= prereqs:
                pass
            else:
                abort(403)

        chal_class = get_chal_class(challenge.type)

        # Anti-bruteforce / submitting Flags too quickly
        kpm = current_user.get_wrong_submissions_per_minute(user.account_id)
        if kpm > 10:
            chal_class.fail(
                user=user, challenge=challenge, request=request
            )
            log(
                "submissions",
                "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [TOO FAST]",
                submission=request_data.get("submission", "").encode("utf-8"),
                challenge_id=challenge_id,
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
            account_id=user.account_id, challenge_id=challenge_id
        ).first()

        # Challenge not solved yet
        if not solves:
            # Hit max attempts
            max_tries = challenge.max_attempts
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

            status, message = chal_class.attempt(challenge, request)
            if status:  # The challenge plugin says the input is right
                chal_class.solve(
                    user=user, challenge=challenge, request=request
                )

                log(
                    "submissions",
                    "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [CORRECT]",
                    submission=request_data.get("submission", "").encode("utf-8"),
                    challenge_id=challenge_id,
                    kpm=kpm,
                )
                return {
                    "success": True,
                    "data": {"status": "correct", "message": message},
                }
            else:  # The challenge plugin says the input is wrong
                chal_class.fail(
                    user=user, challenge=challenge, request=request
                )

                log(
                    "submissions",
                    "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [WRONG]",
                    submission=request_data.get("submission", "").encode("utf-8"),
                    challenge_id=challenge_id,
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

        # Challenge already solved
        else:
            log(
                "submissions",
                "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [ALREADY SOLVED]",
                submission=request_data.get("submission", "").encode("utf-8"),
                challenge_id=challenge_id,
                kpm=kpm,
            )
            return {
                "success": True,
                "data": {
                    "status": "already_solved",
                    "message": "You already solved this",
                },
            }


@challenges_namespace.route("/<challenge_id>/solves")
class ChallengeSolves(Resource):
    @require_verified_emails
    def get(self, challenge_id):
        response = []
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()

        # TODO: Need a generic challenge visibility call.
        # However, it should be stated that a solve on a gated challenge is not considered private.
        if challenge.state == "hidden" and is_admin() is False:
            abort(404)

        Model = get_model()

        solves = (
            Solves.query.join(Model, Solves.account_id == Model.id)
            .filter(
                Solves.challenge_id == challenge_id,
                Model.banned == False,
                Model.hidden == False,
            )
            .order_by(Solves.date.asc())
        )

        for solve in solves:
            response.append(
                {
                    "account_id": solve.account_id,
                    "name": solve.account.name,
                    "date": isoformat(solve.date),
                    "account_url": generate_account_url(account_id=solve.account_id),
                }
            )

        return {"success": True, "data": response}


@challenges_namespace.route("/<challenge_id>/files")
class ChallengeFiles(Resource):
    @contributors_teachers_admins_only
    def get(self, challenge_id):
        response = []
        challenge_files = ChallengeFilesModel.query.filter_by(
            challenge_id=challenge_id
        ).all()

        for f in challenge_files:
            response.append({"id": f.id, "type": f.type, "location": f.location})
        return {"success": True, "data": response}


@challenges_namespace.route("/<challenge_id>/tags")
class ChallengeTags(Resource):
    @contributors_teachers_admins_only
    def get(self, challenge_id):
        response = []
        tags = []

        tag_challenges = TagChallenge.query.filter_by(challenge_id=challenge_id).all()
        for tag_challenge in tag_challenges:
            tags.append(
                Tags.query.filter_by(id=tag_challenge.tag_id).first()
            )
        for t in tags:
            response.append(
                {"id": t.id, "value": t.value}
            )
        return {"success": True, "data": response}


@challenges_namespace.route("/<challenge_id>/hints")
class ChallengeHints(Resource):
    @contributors_teachers_admins_only
    def get(self, challenge_id):
        hints = Hints.query.filter_by(challenge_id=challenge_id).all()
        schema = HintSchema(many=True)
        response = schema.dump(hints)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}


@challenges_namespace.route("/<challenge_id>/votes")
class ChallengeVotes(Resource):
    @contributors_teachers_admins_only
    def get(self, challenge_id):
        response_votes = []
        response_message = "Add vote"

        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        votes = Votes.query.filter_by(challenge_id=challenge_id).all()

        if challenge.state != "voting":
            response_message = "Challenge is not in voting state"
        else:
            user_has_voted = Votes.query.filter_by(challenge_id=challenge.id, user_id=session["id"]).first()
            if challenge.author_id == session["id"]:
                response_message = "You can't vote for your own challenge"
            elif user_has_voted is not None:
                response_message = "Already voted"

        for v in votes:
            # An admin or the voter can edit or delete the vote
            if challenge.state == "voting" and (is_admin() or session["id"] == v.user_id):
                response_votes.append(
                    {
                        "id": v.id,
                        "challenge_id": v.challenge_id,
                        "user_id": v.user_id,
                        "value": v.value,
                        "user_name": v.user.name,
                        "can_be_altered": True,
                    }
                )
            else:
                response_votes.append(
                    {
                        "id": v.id,
                        "challenge_id": v.challenge_id,
                        "user_id": v.user_id,
                        "value": v.value,
                        "user_name": v.user.name,
                        "can_be_altered": False,
                    }
                )

        return {"success": True, "data": {"votes": response_votes, "message": response_message}}


@challenges_namespace.route("/<challenge_id>/flags")
class ChallengeFlags(Resource):
    @contributors_teachers_admins_only
    def get(self, challenge_id):
        flags = Flags.query.filter_by(challenge_id=challenge_id).all()
        schema = FlagSchema(many=True)
        response = schema.dump(flags)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}


@challenges_namespace.route("/<challenge_id>/requirements")
class ChallengeRequirements(Resource):
    @contributors_teachers_admins_only
    def get(self, challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        return {"success": True, "data": challenge.requirements}