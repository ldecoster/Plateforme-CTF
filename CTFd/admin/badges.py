from flask import render_template

from CTFd.admin import admin
from CTFd.models import Badges, Submissions, TagChallenge, Tags
from CTFd.utils.decorators import access_granted_only


@admin.route("/admin/badges")
@access_granted_only("admin_badges_listing")
def badges_listing():
    badges = Badges.query.all()
    return render_template(
        "admin/badges/badges.html",
        badges=badges,
        Badges=Badges,
        Submissions=Submissions,
        TagChallenge=TagChallenge,
        Tags=Tags
    )


@admin.route("/admin/badges/<int:badge_id>")
@access_granted_only("admin_badges_detail")
def badges_detail(badge_id):
    badge = Badges.query.filter_by(id=badge_id).first_or_404()

    return render_template("/admin/badges/badge.html", badge=badge)


@admin.route("/admin/badges/new")
@access_granted_only("admin_badges_new")
def badges_new():
    tags = Tags.query.all()
    return render_template("admin/badges/new.html", tags=tags)

