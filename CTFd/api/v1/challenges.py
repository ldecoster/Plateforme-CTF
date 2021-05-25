from typing import List

from flask import abort, render_template, request, url_for
from flask_restx import Namespace, Resource
from sqlalchemy import func as sa_func
from sqlalchemy.sql import and_, false

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import ChallengeFiles as ChallengeFilesModel
from CTFd.models import (
    Challenges,
    Fails,
    Flags,
    Resources,
    Solves,
    Submissions,
    Tags,
    TagChallenge,
    Users,
    Votes,
    db,
)
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.schemas.challenges import ChallengeSchema
from CTFd.schemas.flags import FlagSchema
from CTFd.schemas.resources import ResourceSchema
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
    access_granted_only,
    require_verified_emails,
)
from CTFd.utils.decorators.visibility import check_challenge_visibility
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.logging import log
from CTFd.utils.modes import generate_account_url, get_model
from CTFd.utils.security.signing import serialize
from CTFd.utils.user import (
    authed,
    get_current_user,
    has_right,
    has_right_or_is_author
)
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


def _build_solves_query(extra_filters=(), admin_view=False):
    """Returns queries and data that that are used for showing an account's solves.
    It returns a tuple of
        - SQLAlchemy query with (challenge_id, solve_count_for_challenge_id)
        - Current user's solved challenge IDs
    """
    # This can return None (unauth) if visibility is set to public
    user = get_current_user()
    # We only set a condition for matching user solves if there is a user and
    # they have an account ID (user mode or in a team in teams mode)
    AccountModel = get_model()
    if user is not None and user.account_id is not None:
        user_solved_cond = Solves.account_id == user.account_id
    else:
        user_solved_cond = false()
    # Finally, we never count solves made by hidden or banned users, even
    # if we are an admin. This is to match the challenge detail API.
    exclude_solves_cond = and_(
        AccountModel.banned == false(), AccountModel.hidden == false(),
    )
    # This query counts the number of solves per challenge, as well as the sum
    # of correct solves made by the current user per the condition above (which
    # should probably only be 0 or 1!)
    solves_q = (
        db.session.query(Solves.challenge_id, sa_func.count(Solves.challenge_id),)
        .join(AccountModel)
        .filter(*extra_filters, exclude_solves_cond)
        .group_by(Solves.challenge_id)
    )
    # Also gather the user's solve items which can be different from above query
    # Even if we are a hidden user, we should see that we have solved the challenge
    # But as a hidden user we are not included in the count
    solve_ids = (
        Solves.query.with_entities(Solves.challenge_id).filter(user_solved_cond).all()
    )
    solve_ids = {value for value, in solve_ids}
    return solves_q, solve_ids


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
            "author_id": (str, None),
            "field": (
                RawEnum(
                    "ChallengeFields",
                    {
                        "name": "name",
                        "description": "description",
                        "type": "type",
                        "state": "state",
                        "author_id": "author_id",
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

        # Admins get a shortcut to see all challenges despite pre-requisites
        admin_view = access_granted_only("api_challenge_list_get_full") and request.args.get("view") == "admin"

        solve_counts = {}
        # Build a query for to show challenge solve information. We only
        # give an admin view if the request argument has been provided.
        #
        # NOTE: This is different behaviour to the challenge detail
        # endpoint which only needs the current user to be an admin rather
        # than also also having to provide `view=admin` as a query arg.
        solves_q, user_solves = _build_solves_query(admin_view=admin_view)
        # Aggregate the query results into the hashes defined at the top of
        # this block for later use
        for chal_id, solve_count in solves_q:
            solve_counts[chal_id] = solve_count
        if accounts_visible():
            solve_count_dfl = 0
        else:
            # Empty out the solves_count if we're hiding scores/accounts
            solve_counts = {}
            # This is necessary to match the challenge detail API which returns
            # `None` for the solve count if visibility checks fail
            solve_count_dfl = None

            # Build the query for the challenges which may be listed
        chal_q = Challenges.query
        # Admins can see hidden challenges in the admin view
        if admin_view is False:
            chal_q = chal_q.filter(
                and_(Challenges.state != "hidden")
            )
        chal_q = (
            chal_q.filter_by(**query_args).filter(*filters)
        )

        # Iterate through the list of challenges, adding to the object which
        # will be JSONified back to the client
        response = []
        tag_schema = TagSchema(view="user", many=True)
        for challenge in chal_q:
            user = Users.query.filter_by(id=challenge.author_id).first();
            if challenge.requirements:
                requirements = challenge.requirements.get("prerequisites", [])
                anonymize = challenge.requirements.get("anonymize")
                prereqs = set(requirements)
                if user_solves >= prereqs:
                    pass
                else:
                    if anonymize:
                        response.append(
                            {
                                "id": challenge.id,
                                "type": "hidden",
                                "name": "???",
                                "solves": None,
                                "solved_by_me": False,
                                "tags": [],
                                "author_name": "",
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
                    "solves": solve_counts.get(challenge.id, solve_count_dfl),
                    "solved_by_me": challenge.id in user_solves,
                    "tags": tag_schema.dump(challenge.tags).data,
                    "author_name": user.name,
                    "template": challenge_type.templates["view"],
                    "script": challenge_type.scripts["view"],
                }
            )

        db.session.close()
        return {"success": True, "data": response}

    @access_granted_only("api_challenge_list_post")
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

        # Load data through schema for validation but not for insertion
        schema = ChallengeSchema()
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge_type = data["type"]
        data["author_id"] = session["id"]
        challenge_class = get_chal_class(challenge_type)
        challenge = challenge_class.create(request)
        response = challenge_class.read(challenge)
        return {"success": True, "data": response}


@challenges_namespace.route("/types")
class ChallengeTypes(Resource):
    @access_granted_only("api_challenge_types_get")
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
        if access_granted_only("api_challenge_get_not_hidden"):
            chal = Challenges.query.filter(Challenges.id == challenge_id).first_or_404()
        else:
            chal = Challenges.query.filter(
                Challenges.id == challenge_id,
                and_(Challenges.state != "hidden"),
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
                solve_ids = {value for value, in solve_ids}
                prereqs = set(requirements)
                if solve_ids >= prereqs or access_granted_only("api_challenge_get"):
                    pass
                else:
                    if anonymize:
                        return {
                            "success": True,
                            "data": {
                                "id": chal.id,
                                "type": "hidden",
                                "name": "???",
                                "solves": None,
                                "solved_by_me": False,
                                "tags": [],
                                "author_name": "",
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

        
        resources = []
        if authed():
            user = get_current_user()

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

        for resource in Resources.query.filter_by(challenge_id=chal.id).all():
           
            resources.append({"id": resource.id , "content": resource.content})

        response = chal_class.read(challenge=chal)

        solves_q, user_solves = _build_solves_query(
            admin_view=has_right("api_challenge_get"), extra_filters=(Solves.challenge_id == chal.id,)
        )
        # If there are no solves for this challenge ID then we have 0 rows
        maybe_row = solves_q.first()
        if maybe_row:
            challenge_id, solve_count = maybe_row
            solved_by_user = challenge_id in user_solves
        else:
            solve_count, solved_by_user = 0, False

        # Hide solve counts if we are hiding solves/accounts
        if accounts_visible() is False:
            solve_count = None

        if authed():
            # Get current attempts for the user
            attempts = Submissions.query.filter_by(
                account_id=user.account_id, challenge_id=challenge_id
            ).count()
        else:
            attempts = 0

        response["solves"] = solve_count
        response["solved_by_me"] = solved_by_user
        response["attempts"] = attempts
        response["files"] = files
        response["tags"] = tags
        response["resources"] = resources

        response["view"] = render_template(
            chal_class.templates["view"].lstrip("/"),
            solves=solve_count,
            solved_by_me=solved_by_user,
            files=files,
            tags=tags,
            resources=[Resources(**h) for h in resources],
            max_attempts=chal.max_attempts,
            attempts=attempts,
            challenge=chal,
        )

        db.session.close()
        return {"success": True, "data": response}

    @access_granted_only("api_challenge_patch")
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
        data = request.get_json()

        # Load data through schema for validation but not for insertion
        schema = ChallengeSchema()
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 40

        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        data = request.form or request.get_json()
        challenge_new_state = None

        # Check state's value to avoid unwanted input from the user
        if 'state' in data:
            challenge_new_state = data['state']
            if challenge_new_state != "visible" and challenge_new_state != "voting" and challenge_new_state != "hidden":
                return {"success": False}

        if has_right("api_challenge_patch_full"):
            challenge_class = get_chal_class(challenge.type)
            challenge = challenge_class.update(challenge, request)
            response = challenge_class.read(challenge)
            return {"success": True, "data": response}
        elif has_right_or_is_author("api_challenge_patch_partial", challenge.author_id):
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

    @challenges_namespace.doc(
        description="Endpoint to delete a specific Challenge object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        if has_right_or_is_author("api_challenge_delete", challenge.author_id):
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

        if current_user.has_right("api_challenge_attempt_post_full"):
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

        if challenge.requirements:
            requirements = challenge.requirements.get("prerequisites", [])
            solve_ids = (
                Solves.query.with_entities(Solves.challenge_id)
                .filter_by(account_id=user.account_id)
                .order_by(Solves.challenge_id.asc())
                .all()
            )
            solve_ids = {solve_id for solve_id, in solve_ids}
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
                name=user.name,
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
                    name=user.name,
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
                    name=user.name,
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
                name=user.name,
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
        if challenge.state == "hidden" and access_granted_only("api_challenge_solves_get") is False:
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
    @access_granted_only("api_challenge_files_get")
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
    @access_granted_only("api_challenge_tags_get")
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
                {"id": t.id, "value": t.value, "exercise": t.exercise}
            )
        return {"success": True, "data": response}


@challenges_namespace.route("/<challenge_id>/resources")
class ChallengeResources(Resource):
    @access_granted_only("api_challenge_resources_get")
    def get(self, challenge_id):
        resources = Resources.query.filter_by(challenge_id=challenge_id).all()
        schema = ResourceSchema(many=True)
        response = schema.dump(resources)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}


@challenges_namespace.route("/<challenge_id>/votes")
class ChallengeVotes(Resource):
    @access_granted_only("api_challenge_votes_get")
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
            if challenge.state == "voting" and (access_granted_only("api_challenge_votes_get_edit_vote") or session["id"] == v.user_id):
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
    @access_granted_only("api_challenge_flags_get")
    def get(self, challenge_id):
        flags = Flags.query.filter_by(challenge_id=challenge_id).all()
        schema = FlagSchema(many=True)
        response = schema.dump(flags)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}


@challenges_namespace.route("/<challenge_id>/requirements")
class ChallengeRequirements(Resource):
    @access_granted_only("api_challenge_requirements_get")
    def get(self, challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        return {"success": True, "data": challenge.requirements}
