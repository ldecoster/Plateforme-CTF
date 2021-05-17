from flask import abort, render_template, request, url_for, session

from CTFd.admin import admin
from CTFd.models import Challenges, Flags, Solves, Tags, TagChallenge, Votes
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.utils.config import get_votes_number
from CTFd.utils.decorators import access_granted_only
from CTFd.utils.user import has_right, has_right_or_is_author
from sqlalchemy.sql import and_, or_


@admin.route("/admin/badges")
@access_granted_only("admin_badges_listing")
def challenges_listing():
    q = request.args.get("q")
    field = request.args.get("field")
    filters = []

    if q:
        # The field exists as an exposed column
        if Challenges.__mapper__.has_property(field):
            if field == "tags":
                query_tag = Tags.query.filter(Tags.value.ilike(q)).first()
                if query_tag is not None:
                    tag_challenges = TagChallenge.query.filter_by(tag_id=query_tag.id).with_entities(TagChallenge.challenge_id)
                    filters.append(Challenges.id.in_(tag_challenges))
                else:
                    filters.append(None)
            else:
                filters.append(getattr(Challenges, field).like("%{}%".format(q)))

    if has_right("admin_challenges_listing_restricted"):
        query = Challenges.query.filter(*filters, or_(
            Challenges.author_id == session["id"],
            and_(Challenges.author_id == session["id"], Challenges.state == "hidden"),
            Challenges.state == "voting"
        )).order_by(Challenges.id.asc())
    else:
        query = Challenges.query.filter(*filters).order_by(Challenges.id.asc())

    challenges = query.all()
    total = query.count()

    return render_template(
        "admin/challenges/challenges.html",
        challenges=challenges,
        total=total,
        q=q,
        field=field,
        Votes=Votes,
    )


@admin.route("/admin/challenges/<int:challenge_id>")
def challenges_detail(challenge_id):
    challenges = dict(
        Challenges.query.with_entities(Challenges.id, Challenges.name).all()
    )
    challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
    if has_right_or_is_author("admin_challenges_detail", challenge.author_id) or challenge.state == "voting":
        solves = (
            Solves.query.filter_by(challenge_id=challenge.id)
                .order_by(Solves.date.asc())
                .all()
        )
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()

        votes = Votes.query.filter_by(challenge_id=challenge.id).all()
        user_has_voted = Votes.query.filter_by(challenge_id=challenge.id, user_id=session["id"]).first()

        votes_delta = get_votes_number()

        try:
            challenge_class = get_chal_class(challenge.type)
        except KeyError:
            abort(
                500,
                f"The underlying challenge type ({challenge.type}) is not installed. This challenge can not be loaded.",
            )

        update_j2 = render_template(
            challenge_class.templates["update"].lstrip("/"), challenge=challenge, votes_delta=votes_delta
        )

        update_script = url_for(
            "views.static_html", route=challenge_class.scripts["update"].lstrip("/")
        )
        return render_template(
            "admin/challenges/challenge.html",
            update_template=update_j2,
            update_script=update_script,
            challenge=challenge,
            challenges=challenges,
            solves=solves,
            flags=flags,
            votes=votes,
            user_has_voted=user_has_voted,
        )
    else:
        abort(403)


@admin.route("/admin/challenges/new")
@access_granted_only("admin_challenges_new")
def challenges_new():
    types = CHALLENGE_CLASSES.keys()
    return render_template("admin/challenges/new.html", types=types)
