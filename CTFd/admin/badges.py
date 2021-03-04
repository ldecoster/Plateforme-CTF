from flask import abort, render_template, request, url_for, session

from CTFd.admin import admin
from CTFd.models import Badges, Flags, Solves, Tags,TagChallenge, Votes
from CTFd.plugins.badges import BADGE_CLASSES, get_badge_class
from CTFd.utils.config import get_votes_number
from CTFd.utils.decorators import contributors_teachers_admins_only
from CTFd.utils.user import is_teacher,is_contributor, is_admin
from sqlalchemy.sql import and_, or_


@admin.route("/admin/badges")
@contributors_teachers_admins_only
def badges_listing():
    q = request.args.get("q")
    field = request.args.get("field")
    filters = []
    tags = Tags.query.all()


    if q:
        # The field exists as an exposed column
        if Badges.__mapper__.has_property(field):
            if field == "tags":
                query_tag = Tags.query.filter(Tags.value.ilike(q)).first()
                if query_tag is not None:
                    tag_badges = TagChallenge.query.filter_by(tag_id=query_tag.id).with_entities(TagChallenge.badge_id)
                    filters.append(Badges.id.in_(tag_badges))
                else:
                    filters.append(None)
            else:
                filters.append(getattr(Badges, field).like("%{}%".format(q)))

    if is_contributor():
        query = Badges.query.filter(*filters, or_(Badges.id==session["id"],and_(Badges.id==session["id"], Badges.state=="hidden"),Badges.state=="voting")).order_by(Badges.id.asc())
    else:
        query = Badges.query.filter(*filters).order_by(Badges.id.asc())

    badges = query.all()
    total = query.count()

    return render_template(
        "admin/badges/badges.html",
        badges=badges,
        total=total,
        q=q,
        field=field,
        Votes=Votes,
        tags= tags,

    )


@admin.route("/admin/badges/<int:badge_id>")
@contributors_teachers_admins_only
def badges_detail(badge_id):
    badges = dict(
        Badges.query.with_entities(Badges.id, Badges.name).all()
    )
    badge = Badges.query.filter_by(id=badge_id).first_or_404()
    if is_admin() or is_teacher() or badge.id == session['id'] or badge.state == "voting":

        try:
            badge_class = get_badge_class(badge.id)
        except KeyError:
            abort(
                500,
                f"The underlying badge type ({badge.id}) is not installed. This badge can not be loaded.",
            )

        update_j2 = render_template(
            badge_class.templates["update"].lstrip("/"), badge=badge
        )

        update_script = url_for(
            "views.static_html", route=badge_class.scripts["update"].lstrip("/")
        )
        return render_template(
            "admin/badges/badge.html",
            update_template=update_j2,
            update_script=update_script,
            badge=badge,
            badges=badges,

        )
    else:
        abort(403)


@admin.route("/admin/badges/badges.html")
@contributors_teachers_admins_only
def badges_new():
    types = BADGE_CLASSES.keys()
    tags = Tags.query.all()
    return render_template("admin/badges/badges.html", types=types, tags=tags)