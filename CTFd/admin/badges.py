from flask import abort, render_template, request, url_for, session

from CTFd.admin import admin
from CTFd.models import Badges, Submissions, Tags, TagChallenge, Users
from CTFd.plugins.badges import get_badge_class, BADGE_CLASSES
from CTFd.utils.decorators import access_granted_only
from CTFd.utils.user import has_right, has_right_or_is_author
from sqlalchemy.sql import and_, or_


@admin.route("/admin/badges")
@access_granted_only("admin_challenges_listing")
def badges_listing():
    q = request.args.get("q")
    field = request.args.get("field")
    return render_template(
        "admin/badges/badges.html",
        q=q,
        field=field,
        Tags=Tags,
        TagChallenge=TagChallenge,
        Submissions=Submissions,
        Badges=Badges,
        Users=Users
    )


@admin.route("/admin/badges/<int:badge_id>")
@access_granted_only("admin_challenges_detail")
def badges_detail(badge_id):
    badges = dict(
        Badges.query.with_entities(Badges.id, Badges.name).all()
    )
    badge = Badges.query.filter_by(id=badge_id).first_or_404()
    if has_right("admin"):
        try:
            badge_class = get_badge_class(badge.type)
        except KeyError:
            abort(
                500,
                f"The underlying challenge type ({badge.type}) is not installed. This challenge can not be loaded.",
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
