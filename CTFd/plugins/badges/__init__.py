from flask import Blueprint

from CTFd.models import (
    ChallengeFiles,
    Challenges,
    Fails,
    Flags,
    Hints,
    Solves,
    TagChallenge,
    Votes,
    Badges,
    db,
)
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.flags import FlagException, get_flag_class
from CTFd.utils.uploads import delete_file
from CTFd.utils.user import get_ip


class BaseBadge(object):
    id = None
    name = None
    templates = {}
    scripts = {}
    badge_model = Badges

    @classmethod
    def create(cls, request):
        """
        This method is used to process the challenge creation request.

        :param request:
        :return:
        """
        data = request.form or request.get_json()

        badge = cls.badge_model(**data)

        db.session.add(badge)
        db.session.commit()

        return badge

    @classmethod
    def read(cls, badge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param badge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        data = {
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            },
        }
        return data

    @classmethod
    def update(cls, badge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.

        :param badge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()
        for attr, value in data.items():
            setattr(badge, attr, value)

        db.session.commit()
        return badge

    @classmethod
    def delete(cls, badge):
        """
        This method is used to delete the resources used by a challenge.

        :param badge:
        :return:
        """
        Badges.query.filter_by(badge_id=badge.id).delete()
        files = ChallengeFiles.query.filter_by(challenge_id=badge.id).all()
        for f in files:
            delete_file(f.id)
        Badges.query.filter_by(id=badge.id).delete()
        cls.badge_model.query.filter_by(id=badge.id).delete()
        db.session.commit()

    @classmethod
    def solve(cls, user, challenge, request):
        """
        This method is used to insert Solves into the database in order to mark a challenge as solved.

        :param user: The User object from the database
        :param challenge: The Challenge object from the database
        :param request: The request the user submitted
        :return:
        """
        data = request.form or request.get_json()
        submission = data["submission"].strip()
        solve = Solves(
            user_id=user.id,
            challenge_id=challenge.id,
            ip=get_ip(req=request),
            provided=submission,
        )
        db.session.add(solve)
        db.session.commit()


class CTFdStandardBadge(BaseBadge):
    id = "standard"  # Unique identifier used to register challenges
    name = "standard"  # Name of a challenge type
    templates = {  # Templates used for each aspect of challenge editing & viewing
        "create": "/plugins/badges/assets/create.html",
        "update": "/plugins/badges/assets/update.html",
        "view": "/plugins/badges/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/badges/assets/create.js",
        "update": "/plugins/badges/assets/update.js",
        "view": "/plugins/badges/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/badges/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "standard", __name__, template_folder="templates", static_folder="assets"
    )
    badge_model = Badges


def get_badge_class(class_id):
    """
    Utility function used to get the corresponding class from a class ID.

    :param class_id: String representing the class ID
    :return: Challenge class
    """
    cls = BADGE_CLASSES.get(class_id)
    if cls is None:
        raise KeyError
    return cls


"""
Global dictionary used to hold all the Challenge Type classes used by CTFd. Insert into this dictionary to register
your Challenge Type.
"""
BADGE_CLASSES = {"standard": CTFdStandardBadge}


def load(app):
    register_plugin_assets_directory(app, base_path="/plugins/badges/assets/")
