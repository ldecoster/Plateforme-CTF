import functools

from flask import abort, jsonify, redirect, request, url_for

from CTFd.cache import cache
from CTFd.utils import get_config
from CTFd.utils import user as current_user
from CTFd.utils.user import authed, has_right
from functools import wraps


def require_authentication_if_config(config_key):
    def _require_authentication_if_config(f):
        @functools.wraps(f)
        def __require_authentication_if_config(*args, **kwargs):
            value = get_config(config_key)
            if value and current_user.authed():
                abort(403)
            else:
                return f(*args, **kwargs)

        return __require_authentication_if_config

    return _require_authentication_if_config


def require_verified_emails(f):
    """
    Decorator to restrict an endpoint to users with confirmed active email addresses
    :param f:
    :return:
    """

    @functools.wraps(f)
    def _require_verified_emails(*args, **kwargs):
        if get_config("verify_emails"):
            if current_user.authed():
                if (
                    current_user.has_right("utils_decorators_require_verified_emails") is False
                    and current_user.is_verified() is False
                ):  # User is not confirmed
                    if request.content_type == "application/json":
                        abort(403)
                    else:
                        return redirect(url_for("auth.confirm"))
        return f(*args, **kwargs)

    return _require_verified_emails


def authed_only(f):
    """
    Decorator that requires the user to be authenticated
    :param f:
    :return:
    """

    @functools.wraps(f)
    def authed_only_wrapper(*args, **kwargs):
        if authed():
            return f(*args, **kwargs)
        else:
            if (
                request.content_type == "application/json"
                or request.accept_mimetypes.best == "text/event-stream"
            ):
                abort(403)
            else:
                abort(403)

    return authed_only_wrapper


def registered_only(f):
    """
    Decorator that requires the user to have a registered account
    :param f:
    :return:
    """

    @functools.wraps(f)
    def _registered_only(*args, **kwargs):
        if authed():
            return f(*args, **kwargs)
        else:
            if (
                request.content_type == "application/json"
                or request.accept_mimetypes.best == "text/event-stream"
            ):
                abort(403)
            else:
                return redirect(url_for("auth.register", next=request.full_path))

    return _registered_only


def ratelimit(method="POST", limit=50, interval=300, key_prefix="rl"):
    def ratelimit_decorator(f):
        @functools.wraps(f)
        def ratelimit_function(*args, **kwargs):
            ip_address = current_user.get_ip()
            key = "{}:{}:{}".format(key_prefix, ip_address, request.endpoint)
            current = cache.get(key)

            if request.method == method:
                if (
                    current and int(current) > limit - 1
                ):  # -1 in order to align expected limit with the real value
                    resp = jsonify(
                        {
                            "code": 429,
                            "message": "Too many requests. Limit is %s requests in %s seconds"
                            % (limit, interval),
                        }
                    )
                    resp.status_code = 429
                    return resp
                else:
                    if current is None:
                        cache.set(key, 1, timeout=interval)
                    else:
                        cache.set(key, int(current) + 1, timeout=interval)
            return f(*args, **kwargs)

        return ratelimit_function

    return ratelimit_decorator


def access_granted_only(right):
    def decorator(f):
        @wraps(f)
        def access_granted_only_wrapper(*args, **kwargs):
            if has_right(right):
                return f(*args, **kwargs)
            else:
                if request.content_type == "application/json":
                    abort(403)
                else:
                    abort(403)
        return access_granted_only_wrapper
    return decorator
