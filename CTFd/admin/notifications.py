from flask import render_template

from CTFd.admin import admin
from CTFd.models import Notifications
from CTFd.utils.decorators import access_granted_only


@admin.route("/admin/notifications")
@access_granted_only("admin_notifications")
def notifications():
    notifs = Notifications.query.order_by(Notifications.id.desc()).all()
    return render_template("admin/notifications.html", notifications=notifs)
