from flask import Blueprint, render_template

from CTFd.utils import config
from CTFd.utils.decorators import (
    require_verified_emails,
)

from CTFd.utils.helpers import get_errors, get_infos

badges = Blueprint("badges", __name__)


@badges.route("/badges", methods=["GET"])
@require_verified_emails
def listing():
    infos = get_infos()
    errors = get_errors()



    return render_template("badges.html", infos=infos, errors=errors)
