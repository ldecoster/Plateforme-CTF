from flask import url_for

from CTFd.models import Users
from CTFd.utils import get_config

USERS_MODE = "users"


def generate_account_url(account_id, admin=False):
    if get_config("user_mode") == USERS_MODE:
        if admin:
            return url_for("admin.users_detail", user_id=account_id)
        else:
            return url_for("users.public", user_id=account_id)


def get_model():
    if get_config("user_mode") == USERS_MODE:
        return Users


def get_mode_as_word(plural=False, capitalize=False):
    if get_config("user_mode") == USERS_MODE:
        word = "user"

    if plural:
        word += "s"
    if capitalize:
        word = word.title()
    return word
