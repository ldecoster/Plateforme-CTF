from flask import render_template

from CTFd.admin import admin
from CTFd.models import Challenges, Fails, Solves, Tracking, Users, db
from CTFd.utils.decorators import access_granted_only
from CTFd.utils.modes import get_model


@admin.route("/admin/statistics", methods=["GET"])
@access_granted_only("admin_statistics")
def statistics():
    Model = get_model()

    users_registered = Users.query.count()

    wrong_count = (
        Fails.query.join(Model, Fails.account_id == Model.id)
        .filter(Model.banned == False, Model.hidden == False)
        .count()
    )

    solve_count = (
        Solves.query.join(Model, Solves.account_id == Model.id)
        .filter(Model.banned == False, Model.hidden == False)
        .count()
    )

    challenge_count = Challenges.query.count()

    ip_count = Tracking.query.with_entities(Tracking.ip).distinct().count()

    solves_sub = (
        db.session.query(
            Solves.challenge_id, db.func.count(Solves.challenge_id).label("solves_cnt")
        )
        .join(Model, Solves.account_id == Model.id)
        .filter(Model.banned == False, Model.hidden == False)
        .group_by(Solves.challenge_id)
        .subquery()
    )

    solves = (
        db.session.query(
            solves_sub.columns.challenge_id,
            solves_sub.columns.solves_cnt,
            Challenges.name,
        )
        .join(Challenges, solves_sub.columns.challenge_id == Challenges.id)
        .all()
    )

    solve_data = {}
    for _chal, count, name in solves:
        solve_data[name] = count

    most_solved = None
    least_solved = None
    if len(solve_data):
        most_solved = max(solve_data, key=solve_data.get)
        least_solved = min(solve_data, key=solve_data.get)

    db.session.close()

    return render_template(
        "admin/statistics.html",
        user_count=users_registered,
        ip_count=ip_count,
        wrong_count=wrong_count,
        solve_count=solve_count,
        challenge_count=challenge_count,
        solve_data=solve_data,
        most_solved=most_solved,
        least_solved=least_solved,
    )
