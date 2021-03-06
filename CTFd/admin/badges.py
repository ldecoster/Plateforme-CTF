from flask import abort, render_template, request, url_for, session

from CTFd.admin import admin
from CTFd.models import Badges, Flags, Solves, Tags,TagChallenge, Votes
from CTFd.utils.config import get_votes_number
from CTFd.utils.decorators import contributors_teachers_admins_only
from CTFd.utils.user import is_teacher,is_contributor, is_admin
from sqlalchemy.sql import and_, or_


@admin.route("/admin/badges")
@contributors_teachers_admins_only
def badges_listing():
    q = request.args.get("q")
    field = request.args.get("field")
    badges = Badges.query.all()

    return render_template(
        "admin/badges/badges.html",
        badges=badges,
        q=q,
        field=field,
        Tags= Tags,
    )


@admin.route("/admin/badges/<int:badge_id>")
@contributors_teachers_admins_only
def badges_detail(badge_id):
    badges = dict(
        Badges.query.with_entities(Badges.id, Badges.name).all()
    )
    badge = Badges.query.filter_by(id=badge_id).first_or_404()
    if is_admin() or is_teacher() or badge.id == session['id'] or badge.state == "voting":

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
