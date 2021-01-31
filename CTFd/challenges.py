from flask import Blueprint, render_template

from CTFd.utils import config
from CTFd.utils.dates import ctf_paused
from CTFd.utils.decorators import require_verified_emails
from CTFd.utils.decorators.visibility import check_challenge_visibility
from CTFd.utils.helpers import get_errors, get_infos

challenges = Blueprint("challenges", __name__)


@challenges.route("/challenges", methods=["GET"])
@require_verified_emails
@check_challenge_visibility
def listing():
    infos = get_infos()
    errors = get_errors()

    if ctf_paused() is True:
        infos.append(f"{config.ctf_name()} is paused")

    return render_template("challenges.html", infos=infos, errors=errors)
