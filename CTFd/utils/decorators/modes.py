import functools


def require_user_mode(f):
    @functools.wraps(f)
    def _require_user_mode(*args, **kwargs):
        return f(*args, **kwargs)

    return _require_user_mode
