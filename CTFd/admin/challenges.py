from flask import abort, render_template, request, url_for, session

from CTFd.admin import admin


from CTFd.models import Challenges, Flags, Solves, Votes
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.utils.config import get_votes_number
from CTFd.utils.decorators import contributors_contributors_plus_admins_only
from CTFd.utils.user import is_teacher,is_contributor, is_admin
from sqlalchemy.sql import and_, or_


@admin.route("/admin/challenges")
@contributors_contributors_plus_admins_only
def challenges_listing():
    q = request.args.get("q")
    field = request.args.get("field")
    filters = []

    if q:
        # The field exists as an exposed column
        if Challenges.__mapper__.has_property(field):
            filters.append(getattr(Challenges, field).like("%{}%".format(q)))
    if is_contributor():
        query = Challenges.query.filter(*filters, or_(Challenges.author_id==session["id"],and_(Challenges.author_id==session["id"], Challenges.state=="hidden"),Challenges.state=="vote")).order_by(Challenges.id.asc())
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
@contributors_contributors_plus_admins_only
def challenges_detail(challenge_id):
    challenges = dict(
        Challenges.query.with_entities(Challenges.id, Challenges.name).all()
    )
    challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
    #author = Users.query.filter_by(id=challenge.author_id).first_or_404()
    if is_admin() or is_teacher() or challenge.author_id == session['id'] or challenge.state == "vote":
        solves = (
            Solves.query.filter_by(challenge_id=challenge.id)
            .order_by(Solves.date.asc())
            .all()
        )
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()

        votes = Votes.query.filter_by(challenge_id=challenge.id).all()

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
        )
    else:
        abort(403)


@admin.route("/admin/challenges/new")
@contributors_contributors_plus_admins_only
def challenges_new():
    types = CHALLENGE_CLASSES.keys()
    return render_template("admin/challenges/new.html", types=types)
