from flask import Blueprint, render_template, request, url_for

from CTFd.models import Users
from CTFd.utils.decorators import authed_only
from CTFd.utils.decorators.visibility import check_account_visibility
from CTFd.utils.helpers import get_errors, get_infos
from CTFd.utils.user import get_current_user
from flask import jsonify
import json 
import sqlite3
import select

users = Blueprint("users", __name__)


@users.route("/users")
@check_account_visibility
def listing():
    q = request.args.get("q")
    field = request.args.get("field", "name")
    if field not in ("name", "website"):
        field = "name"

    filters = []
    if q:
        filters.append(getattr(Users, field).like("%{}%".format(q)))

    users = (
        Users.query.filter_by(banned=False, hidden=False)
        .filter(*filters)
        .order_by(Users.id.asc())
        .paginate(per_page=50)
    )
    
    args = dict(request.args)
    args.pop("page", 1)
    
    #Convert database result in json
    DB = "C:/Users/Solène/Documents/GitKraken/Plateforme-CTF/CTFd/ctfd.db"
    def get_all_users(json_str = False):
        conn = sqlite3.connect( DB )
        conn.row_factory = sqlite3.Row
        db = conn.cursor()

        rows = db.execute('''SELECT * from Users''').fetchall()

        conn.commit
        conn.close()

        if json_str:
            return json.dumps([dict(ix) for ix in rows], indent=0)
        
        return rows
    
    data = get_all_users(json_str=True)
    with open('data.json', 'w') as f:
        f.write(data)


    return render_template(
        "users/users.html",
        users=users,
        prev_page=url_for(request.endpoint, page=users.prev_num, **args),
        next_page=url_for(request.endpoint, page=users.next_num, **args),
        q=q,
        field=field,
    )


@users.route("/profile")
@users.route("/user")
@authed_only
def private():
    infos = get_infos()
    errors = get_errors()

    user = get_current_user()

    return render_template(
        "users/private.html",
        user=user,
        account=user.account,
        infos=infos,
        errors=errors,
    )


@users.route("/users/<int:user_id>")
@check_account_visibility
def public(user_id):
    infos = get_infos()
    errors = get_errors()
    user = Users.query.filter_by(id=user_id, banned=False, hidden=False).first_or_404()

    return render_template(
        "users/public.html", user=user, account=user.account, infos=infos, errors=errors
    )
