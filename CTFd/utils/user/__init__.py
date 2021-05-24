import datetime
import re

from flask import abort
from flask import current_app as app
from flask import redirect, request, session, url_for

from CTFd.cache import cache
from CTFd.constants.users import UserAttrs
from CTFd.models import Badges, Challenges, Fails, Solves, TagChallenge, Tracking, Rights, UserRights, Users, db
from CTFd.utils import get_config
from CTFd.utils.security.auth import logout_user
from CTFd.utils.security.signing import hmac


def get_current_user():
    if authed():
        user = Users.query.filter_by(id=session["id"]).first()

        # Check if the session is still valid
        session_hash = session.get("hash")
        if session_hash:
            if session_hash != hmac(user.password):
                logout_user()
                if request.content_type == "application/json":
                    error = 401
                else:
                    error = redirect(url_for("auth.login", next=request.full_path))
                abort(error)

        return user
    else:
        return None


def get_current_user_attrs():
    if authed():
        return get_user_attrs(user_id=session["id"])
    else:
        return None


@cache.memoize(timeout=300)
def get_user_attrs(user_id):
    user = Users.query.filter_by(id=user_id).first()
    if user:
        d = {}
        for field in UserAttrs._fields:
            d[field] = getattr(user, field)
        return UserAttrs(**d)
    return None


def get_current_user_type(fallback=None):
    if authed():
        user = get_current_user_attrs()
        return user.type
    else:
        return fallback


def authed():
    return bool(session.get("id", False))


def has_right(right_name):
    right = Rights.query.filter_by(name=right_name).first()
    if right is not None and session.get("id"):
        user_rights = UserRights.query.filter_by(right_id=right.id, user_id=session["id"]).first()
        if user_rights is not None:
            return True
    return False


def has_right_or_is_author(right_name, author_id):
    right = Rights.query.filter_by(name=right_name).first()
    if right is not None and session.get("id"):
        user_rights = UserRights.query.filter_by(right_id=right.id, user_id=session["id"]).first()
        if user_rights is not None or author_id == session["id"]:
            return True
    return False


def is_verified():
    if get_config("verify_emails"):
        user = get_current_user_attrs()
        if user:
            return user.verified
        else:
            return False
    else:
        return True


def get_ip(req=None):
    """ Returns the IP address of the currently in scope request. The approach is to define a list of trusted proxies
     (in this case the local network), and only trust the most recently defined untrusted IP address.
     Taken from http://stackoverflow.com/a/22936947/4285524 but the generator there makes no sense.
     The trusted_proxies regexes is taken from Ruby on Rails.

     This has issues if the clients are also on the local network so you can remove proxies from config.py.

     CTFd does not use IP address for anything besides cursory tracking of teams and it is ill-advised to do much
     more than that if you do not know what you're doing.
    """
    if req is None:
        req = request
    trusted_proxies = app.config["TRUSTED_PROXIES"]
    combined = "(" + ")|(".join(trusted_proxies) + ")"
    route = req.access_route + [req.remote_addr]
    for addr in reversed(route):
        if not re.match(combined, addr):  # IP is not trusted but we trust the proxies
            remote_addr = addr
            break
    else:
        remote_addr = req.remote_addr
    return remote_addr


def get_current_user_recent_ips():
    if authed():
        return get_user_recent_ips(user_id=session["id"])
    else:
        return None


@cache.memoize(timeout=300)
def get_user_recent_ips(user_id):
    hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    addrs = (
        Tracking.query.with_entities(Tracking.ip.distinct())
        .filter(Tracking.user_id == user_id, Tracking.date >= hour_ago)
        .all()
    )
    return {ip for (ip,) in addrs}


def get_wrong_submissions_per_minute(account_id):
    """
    Get incorrect submissions per minute.

    :param account_id:
    :return:
    """
    one_min_ago = datetime.datetime.utcnow() + datetime.timedelta(minutes=-1)
    fails = (
        db.session.query(Fails)
        .filter(Fails.account_id == account_id, Fails.date >= one_min_ago)
        .all()
    )
    return len(fails)


def get_user_badges(user_id):
    user = Users.query.filter_by(id=user_id).first()
    if user:
        solved_chal = TagChallenge.query.join(
            Badges, Badges.tag_id == TagChallenge.tag_id
        ).with_entities(
            TagChallenge.challenge_id
        ).join(
            Solves, Solves.challenge_id == TagChallenge.challenge_id
        ).filter_by(user_id=user.id).all()

        badges_chal = TagChallenge.query.join(
            Badges, Badges.tag_id == TagChallenge.tag_id
        ).with_entities(
            TagChallenge.challenge_id
        ).join(
            Challenges, Challenges.id == TagChallenge.challenge_id
        ).filter_by(state="visible").all()

        solved_chal = [value for (value,) in solved_chal]
        badges_chal = [value for (value,) in badges_chal]

        set_difference = set(badges_chal) - set(solved_chal)
        list_difference = list(set_difference)

        unearned_badges = Badges.query.join(
            TagChallenge, TagChallenge.tag_id == Badges.tag_id
        ).with_entities(
            Badges.id
        ).filter(TagChallenge.challenge_id.in_(list_difference))

        badges = Badges.query.filter(Badges.id.notin_(unearned_badges)).all()
        return badges
    else:
        return None
