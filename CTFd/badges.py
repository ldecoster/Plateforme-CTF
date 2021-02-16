from flask import Blueprint, render_template

from CTFd.utils import config
from CTFd.utils.dates import ctf_ended, ctf_paused, ctf_started
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_verified_emails,
)

from CTFd.utils.helpers import get_errors, get_infos

badges = Blueprint("badges", __name__)


@badges.route("/badges", methods=["GET"])
@during_ctf_time_only
@require_verified_emails
def listing():
    infos = get_infos()
    errors = get_errors()

    if ctf_started() is False:
        errors.append(f"{config.ctf_name()} has not started yet")

    if ctf_paused() is True:
        infos.append(f"{config.ctf_name()} is paused")

    if ctf_ended() is True:
        infos.append(f"{config.ctf_name()} has ended")

    return render_template("badges.html", infos=infos, errors=errors)
