import functools

from flask import abort, redirect, request, url_for

from CTFd.constants.config import (
    AccountVisibilityTypes,
    ChallengeVisibilityTypes,
    ConfigTypes,
    RegistrationVisibilityTypes,
)
from CTFd.utils import get_config
from CTFd.utils.user import authed, has_right


def check_challenge_visibility(f):
    @functools.wraps(f)
    def _check_challenge_visibility(*args, **kwargs):
        v = get_config(ConfigTypes.CHALLENGE_VISIBILITY)
        if v == ChallengeVisibilityTypes.PUBLIC:
            return f(*args, **kwargs)

        elif v == ChallengeVisibilityTypes.PRIVATE:
            if authed():
                return f(*args, **kwargs)
            else:
                if request.content_type == "application/json":
                    abort(403)
                else:
                    return redirect(url_for("auth.login", next=request.full_path))

        elif v == ChallengeVisibilityTypes.ADMINS:
            if has_right("utils_decorators_visibility_check_challenge_visibility"):
                return f(*args, **kwargs)
            else:
                if authed():
                    abort(403)
                else:
                    return redirect(url_for("auth.login", next=request.full_path))

    return _check_challenge_visibility


def check_account_visibility(f):
    @functools.wraps(f)
    def _check_account_visibility(*args, **kwargs):
        v = get_config(ConfigTypes.ACCOUNT_VISIBILITY)
        if v == AccountVisibilityTypes.PUBLIC:
            return f(*args, **kwargs)

        elif v == AccountVisibilityTypes.PRIVATE:
            if authed():
                return f(*args, **kwargs)
            else:
                if request.content_type == "application/json":
                    abort(403)
                else:
                    return redirect(url_for("auth.login", next=request.full_path))

        elif v == AccountVisibilityTypes.ADMINS:
            if has_right("utils_decorators_visibility_check_account_visibility"):
                return f(*args, **kwargs)
            else:
                abort(404)

    return _check_account_visibility


def check_registration_visibility(f):
    @functools.wraps(f)
    def _check_registration_visibility(*args, **kwargs):
        v = get_config(ConfigTypes.REGISTRATION_VISIBILITY)
        if v == RegistrationVisibilityTypes.PUBLIC:
            return f(*args, **kwargs)
        elif v == RegistrationVisibilityTypes.PRIVATE:
            abort(404)

    return _check_registration_visibility
