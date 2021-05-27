import os

from flask import current_app as app

from CTFd.constants.themes import DEFAULT_THEME
from CTFd.utils import get_app_config, get_config


def ctf_name():
    name = get_config("ctf_name")
    return name if name else "CTFd"


def ctf_logo():
    return get_config("ctf_logo")


def ctf_theme():
    theme = get_config("ctf_theme")
    return theme if theme else ""


def ctf_theme_candidates():
    yield ctf_theme()
    if bool(get_app_config("THEME_FALLBACK")):
        yield DEFAULT_THEME


def is_setup():
    return bool(get_config("setup")) is True


def get_votes_number():
    return get_config("votes_number_delta")


def can_send_mail():
    return mailserver() or mailgun()


def get_mail_provider():
    if get_config("mail_server") and get_config("mail_port"):
        return "smtp"
    if get_config("mailgun_api_key") and get_config("mailgun_base_url"):
        return "mailgun"
    if app.config.get("MAIL_SERVER") and app.config.get("MAIL_PORT"):
        return "smtp"
    if app.config.get("MAILGUN_API_KEY") and app.config.get("MAILGUN_BASE_URL"):
        return "mailgun"


def mailgun():
    if app.config.get("MAILGUN_API_KEY") and app.config.get("MAILGUN_BASE_URL"):
        return True
    if get_config("mailgun_api_key") and get_config("mailgun_base_url"):
        return True
    return False


def mailserver():
    if app.config.get("MAIL_SERVER") and app.config.get("MAIL_PORT"):
        return True
    if get_config("mail_server") and get_config("mail_port"):
        return True
    return False


def get_themes():
    dir = os.path.join(app.root_path, "themes")
    return [
        name
        for name in os.listdir(dir)
        if os.path.isdir(os.path.join(dir, name)) and name != "admin"
    ]
