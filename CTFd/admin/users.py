from flask import render_template, request, url_for
from sqlalchemy.sql import not_

from CTFd.admin import admin
from CTFd.models import Challenges, Tags, Tracking, Users
from CTFd.utils.decorators import access_granted_only
from CTFd.utils.user import get_user_badges


@admin.route("/admin/users")
@access_granted_only("admin_user_listing")
def users_listing():
    q = request.args.get("q")
    field = request.args.get("field")
    page = abs(request.args.get("page", 1, type=int))
    filters = []
    users = []

    if q:
        # The field exists as an exposed column
        if Users.__mapper__.has_property(field):
            filters.append(getattr(Users, field).like("%{}%".format(q)))

    if q and field == "ip":
        users = (
            Users.query.join(Tracking, Users.id == Tracking.user_id)
            .filter(Tracking.ip.like("%{}%".format(q)))
            .order_by(Users.id.asc())
            .paginate(page=page, per_page=50)
        )
    else:
        users = (
            Users.query.filter(*filters)
            .order_by(Users.id.asc())
            .paginate(page=page, per_page=50)
        )

    args = dict(request.args)
    args.pop("page", 1)

    return render_template(
        "admin/users/users.html",
        users=users,
        prev_page=url_for(request.endpoint, page=users.prev_num, **args),
        next_page=url_for(request.endpoint, page=users.next_num, **args),
        q=q,
        field=field,
    )


@admin.route("/admin/users/new")
@access_granted_only("admin_users_new")
def users_new():
    return render_template("admin/users/new.html")


@admin.route("/admin/users/<int:user_id>")
@access_granted_only("admin_users_detail")
def users_detail(user_id):
    # Get user object
    user = Users.query.filter_by(id=user_id).first_or_404()

    # Get the user's solves
    solves = user.get_solves()

    # Get challenges that the user is missing
    all_solves = user.get_solves()

    solve_ids = [s.challenge_id for s in all_solves]
    missing = Challenges.query.filter(not_(Challenges.id.in_(solve_ids))).all()

    # Get IP addresses that the User has used
    addrs = (
        Tracking.query.filter_by(user_id=user_id).order_by(Tracking.date.desc()).all()
    )

    # Get Fails
    fails = user.get_fails()

    # Get Badges
    badges = get_user_badges(user_id)

    return render_template(
        "admin/users/user.html",
        solves=solves,
        user=user,
        addrs=addrs,
        missing=missing,
        fails=fails,
        badges=badges,
        Tags=Tags,
    )
