from flask import request
from flask_caching import Cache

cache = Cache()


def make_cache_key(path=None, key_prefix="view/%s"):
    """
    This function mostly emulates Flask-Caching's `make_cache_key` function so we can delete cached api responses.
    Over time this function may be replaced with a cleaner custom cache implementation.
    :param path:
    :param key_prefix:
    :return:
    """
    if path is None:
        path = request.endpoint
    cache_key = key_prefix % path
    return cache_key


def clear_config():
    from CTFd.utils import _get_config, get_app_config

    cache.delete_memoized(_get_config)
    cache.delete_memoized(get_app_config)


def clear_pages():
    from CTFd.utils.config.pages import get_page, get_pages

    cache.delete_memoized(get_pages)
    cache.delete_memoized(get_page)


def clear_user_recent_ips(user_id):
    from CTFd.utils.user import get_user_recent_ips

    cache.delete_memoized(get_user_recent_ips, user_id=user_id)


def clear_user_session(user_id):
    from CTFd.utils.user import get_user_attrs

    cache.delete_memoized(get_user_attrs, user_id=user_id)


def clear_all_user_sessions():
    from CTFd.utils.user import get_user_attrs

    cache.delete_memoized(get_user_attrs)
