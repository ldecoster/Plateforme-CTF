import datetime
from collections import defaultdict

from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property, validates

db = SQLAlchemy()
ma = Marshmallow()


def get_class_by_tablename(tablename):
    """Return class reference mapped to table.
    https://stackoverflow.com/a/23754464

    :param tablename: String with name of table.
    :return: Class reference or None.
    """
    for c in db.Model._decl_class_registry.values():
        if hasattr(c, "__tablename__") and c.__tablename__ == tablename:
            return c
    return None


class Votes(db.Model):
    __tablename__ = "votes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"))
    value = db.Column(db.Boolean, default=False)

    user = db.relationship("Users", foreign_keys="Votes.user_id", lazy="select")


class Badges(db.Model):
    __tablename__ = "badges"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    name = db.Column(db.String(80))
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Badges, self).__init__(**kwargs)


class Notifications(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    user = db.relationship("Users", foreign_keys="Notifications.user_id", lazy="select")

    @property
    def html(self):
        from CTFd.utils.config.pages import build_html
        from CTFd.utils.helpers import markup

        return markup(build_html(self.content))

    def __init__(self, *args, **kwargs):
        super(Notifications, self).__init__(**kwargs)


class Pages(db.Model):
    __tablename__ = "pages"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    route = db.Column(db.String(128), unique=True)
    content = db.Column(db.Text)
    draft = db.Column(db.Boolean)
    hidden = db.Column(db.Boolean)
    auth_required = db.Column(db.Boolean)
    # TODO: Use hidden attribute

    files = db.relationship("PageFiles", backref="page")

    def __init__(self, *args, **kwargs):
        super(Pages, self).__init__(**kwargs)

    def __repr__(self):
        return "<Pages {0}>".format(self.route)


class Challenges(db.Model):
    __tablename__ = "challenges"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    max_attempts = db.Column(db.Integer, default=0)
    type = db.Column(db.String(80))
    state = db.Column(db.String(80), nullable=False, default="visible")
    requirements = db.Column(db.JSON)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    files = db.relationship("ChallengeFiles", backref="challenge")
    resources = db.relationship("Resources", backref="challenge")
    tags = db.relationship("Tags", secondary="tag_challenge")
    flags = db.relationship("Flags", backref="challenge")
    comments = db.relationship("ChallengeComments", backref="challenge")
    author = db.relationship("Users", foreign_keys="Challenges.author_id", lazy="select")

    class alt_defaultdict(defaultdict):
        """
        This slightly modified defaultdict is intended to allow SQLAlchemy to
        not fail when querying Challenges that contain a missing challenge type.

        e.g. Challenges.query.all() should not fail if `type` is `a_missing_type`
        """

        def __missing__(self, key):
            return self["standard"]

    __mapper_args__ = {
        "polymorphic_identity": "standard",
        "polymorphic_on": type,
        "_polymorphic_map": alt_defaultdict(),
    }

    @property
    def html(self):
        from CTFd.utils.config.pages import build_html
        from CTFd.utils.helpers import markup

        return markup(build_html(self.description))

    def __init__(self, *args, **kwargs):
        super(Challenges, self).__init__(**kwargs)

    def __repr__(self):
        return "<Challenge %r>" % self.name


class Resources(db.Model):
    __tablename__ = "resources"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80), default="standard")
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )
    content = db.Column(db.Text)

    __mapper_args__ = {"polymorphic_identity": "standard", "polymorphic_on": type}

    @property
    def name(self):
        return "Resource {id}".format(id=self.id)

    @property
    def category(self):
        return self.__tablename__

    @property
    def description(self):
        return "Resource for {name}".format(name=self.challenge.name)

    @property
    def html(self):
        from CTFd.utils.config.pages import build_html
        from CTFd.utils.helpers import markup

        return markup(build_html(self.content))

    def __init__(self, *args, **kwargs):
        super(Resources, self).__init__(**kwargs)

    def __repr__(self):
        return "<Resource %r>" % self.content


class Tags(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(80))
    exercise = db.Column(db.Boolean)
    challenges = db.relationship("Challenges", secondary="tag_challenge")

    def __init__(self, *args, **kwargs):
        super(Tags, self).__init__(**kwargs)


class TagChallenge(db.Model):
    __tablename__ = "tag_challenge"
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"),
                             primary_key=True, nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super(TagChallenge, self).__init__(**kwargs)


class Files(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80), default="standard")
    location = db.Column(db.Text)

    __mapper_args__ = {"polymorphic_identity": "standard", "polymorphic_on": type}

    def __init__(self, *args, **kwargs):
        super(Files, self).__init__(**kwargs)

    def __repr__(self):
        return "<File type={type} location={location}>".format(
            type=self.type, location=self.location
        )


class ChallengeFiles(Files):
    __mapper_args__ = {"polymorphic_identity": "challenge"}
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )

    def __init__(self, *args, **kwargs):
        super(ChallengeFiles, self).__init__(**kwargs)


class PageFiles(Files):
    __mapper_args__ = {"polymorphic_identity": "page"}
    page_id = db.Column(db.Integer, db.ForeignKey("pages.id"))

    def __init__(self, *args, **kwargs):
        super(PageFiles, self).__init__(**kwargs)


class Flags(db.Model):
    __tablename__ = "flags"
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )
    type = db.Column(db.String(80))
    content = db.Column(db.Text)
    data = db.Column(db.Text)

    __mapper_args__ = {"polymorphic_on": type}

    def __init__(self, *args, **kwargs):
        super(Flags, self).__init__(**kwargs)

    def __repr__(self):
        return "<Flag {0} for challenge {1}>".format(self.content, self.challenge_id)


class Users(db.Model):
    __tablename__ = "users"
    __table_args__ = (db.UniqueConstraint("id"), {})
    # Core attributes
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    type = db.Column(db.String(80))
    secret = db.Column(db.String(128))

    # Supplementary attributes
    website = db.Column(db.String(128))
    country = db.Column(db.String(32))
    school = db.Column(db.String(32))
    cursus = db.Column(db.String(128))
    specialisation = db.Column(db.String(128))
    bracket = db.Column(db.String(32))
    hidden = db.Column(db.Boolean, default=False)
    banned = db.Column(db.Boolean, default=False)
    verified = db.Column(db.Boolean, default=False)

    field_entries = db.relationship(
        "UserFieldEntries", foreign_keys="UserFieldEntries.user_id", lazy="joined"
    )

    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    __mapper_args__ = {"polymorphic_identity": "user", "polymorphic_on": type}

    def __init__(self, **kwargs):
        super(Users, self).__init__(**kwargs)

    @validates("password")
    def validate_password(self, key, plaintext):
        from CTFd.utils.crypto import hash_password

        return hash_password(str(plaintext))

    @hybrid_property
    def account_id(self):
        return self.id

    @hybrid_property
    def account(self):
        return self

    @property
    def fields(self):
        return self.get_fields(admin=False)

    @property
    def solves(self):
        return self.get_solves()

    @property
    def fails(self):
        return self.get_fails()

    def get_fields(self, admin=False):
        if admin:
            return self.field_entries

        return [
            entry for entry in self.field_entries if entry.field.public and entry.value
        ]

    def get_solves(self):
        solves = Solves.query.filter_by(user_id=self.id)
        return solves.all()

    def get_fails(self):
        fails = Fails.query.filter_by(user_id=self.id)
        return fails.all()


class Admins(Users):
    __tablename__ = "admins"
    __mapper_args__ = {"polymorphic_identity": "admin"}


class Contributors(Users):
    __tablename__ = "contributors"
    __mapper_args__ = {"polymorphic_identity": "contributor"}


class Teachers(Users):
    __tablename__ = "teachers"
    __mapper_args__ = {"polymorphic_identity": "teacher"}


class Submissions(db.Model):
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    ip = db.Column(db.String(46))
    provided = db.Column(db.Text)
    type = db.Column(db.String(32))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = db.relationship("Users", foreign_keys="Submissions.user_id", lazy="select")
    challenge = db.relationship(
        "Challenges", foreign_keys="Submissions.challenge_id", lazy="select"
    )

    __mapper_args__ = {"polymorphic_on": type}

    @hybrid_property
    def account_id(self):
        return self.user_id

    @hybrid_property
    def account(self):
        return self.user

    @staticmethod
    def get_child(type):
        child_classes = {
            x.polymorphic_identity: x.class_
            for x in Submissions.__mapper__.self_and_descendants
        }
        return child_classes[type]

    def __repr__(self):
        return f"<Submission id={self.id}, challenge_id={self.challenge_id}, ip={self.ip}, provided={self.provided}>"


class Solves(Submissions):
    __tablename__ = "solves"
    __table_args__ = (
        db.UniqueConstraint("challenge_id", "user_id"),
        {},
    )
    id = db.Column(
        None, db.ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True
    )
    challenge_id = column_property(
        db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")),
        Submissions.challenge_id,
    )
    user_id = column_property(
        db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE")),
        Submissions.user_id,
    )

    user = db.relationship("Users", foreign_keys="Solves.user_id", lazy="select")
    challenge = db.relationship(
        "Challenges", foreign_keys="Solves.challenge_id", lazy="select"
    )

    __mapper_args__ = {"polymorphic_identity": "correct"}


class Fails(Submissions):
    __mapper_args__ = {"polymorphic_identity": "incorrect"}


class Tracking(db.Model):
    __tablename__ = "tracking"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(46))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship("Users", foreign_keys="Tracking.user_id", lazy="select")

    def __init__(self, *args, **kwargs):
        super(Tracking, self).__init__(**kwargs)

    def __repr__(self):
        return "<Tracking %r>" % self.ip


class Configs(db.Model):
    __tablename__ = "config"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text)
    value = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(Configs, self).__init__(**kwargs)


class Tokens(db.Model):
    __tablename__ = "tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expiration = db.Column(
        db.DateTime,
        default=lambda: datetime.datetime.utcnow() + datetime.timedelta(days=30),
    )
    value = db.Column(db.String(128), unique=True)

    user = db.relationship("Users", foreign_keys="Tokens.user_id", lazy="select")

    def __init__(self, *args, **kwargs):
        super(Tokens, self).__init__(**kwargs)

    def __repr__(self):
        return "<Token %r>" % self.id


class UserTokens(Tokens):
    __mapper_args__ = {"polymorphic_identity": "user"}


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80), default="standard")
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    author = db.relationship("Users", foreign_keys="Comments.author_id", lazy="select")

    @property
    def html(self):
        from CTFd.utils.config.pages import build_html
        from CTFd.utils.helpers import markup

        return markup(build_html(self.content, sanitize=True))

    __mapper_args__ = {"polymorphic_identity": "standard", "polymorphic_on": type}


class ChallengeComments(Comments):
    __mapper_args__ = {"polymorphic_identity": "challenge"}
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )


class UserComments(Comments):
    __mapper_args__ = {"polymorphic_identity": "user"}
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))


class PageComments(Comments):
    __mapper_args__ = {"polymorphic_identity": "page"}
    page_id = db.Column(db.Integer, db.ForeignKey("pages.id", ondelete="CASCADE"))


class Fields(db.Model):
    __tablename__ = "fields"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    type = db.Column(db.String(80), default="standard")
    field_type = db.Column(db.String(80))
    description = db.Column(db.Text)
    required = db.Column(db.Boolean, default=False)
    public = db.Column(db.Boolean, default=False)
    editable = db.Column(db.Boolean, default=False)

    __mapper_args__ = {"polymorphic_identity": "standard", "polymorphic_on": type}


class UserFields(Fields):
    __mapper_args__ = {"polymorphic_identity": "user"}


class FieldEntries(db.Model):
    __tablename__ = "field_entries"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80), default="standard")
    value = db.Column(db.JSON)
    field_id = db.Column(db.Integer, db.ForeignKey("fields.id", ondelete="CASCADE"))

    field = db.relationship(
        "Fields", foreign_keys="FieldEntries.field_id", lazy="joined"
    )

    __mapper_args__ = {"polymorphic_identity": "standard", "polymorphic_on": type}

    @hybrid_property
    def name(self):
        return self.field.name

    @hybrid_property
    def description(self):
        return self.field.description


class UserFieldEntries(FieldEntries):
    __mapper_args__ = {"polymorphic_identity": "user"}
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    user = db.relationship("Users", foreign_keys="UserFieldEntries.user_id")


class Rights(db.Model):
    __tablename__ = "rights"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(Rights, self).__init__(**kwargs)


class Roles(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(Roles, self).__init__(**kwargs)


class RoleRights(db.Model):
    __tablename__ = "role_rights"
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    right_id = db.Column(db.Integer, db.ForeignKey("rights.id", ondelete="CASCADE"), primary_key=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super(RoleRights, self).__init__(**kwargs)


class UserRights(db.Model):
    __tablename__ = "user_rights"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    right_id = db.Column(db.Integer, db.ForeignKey("rights.id", ondelete="CASCADE"), primary_key=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super(UserRights, self).__init__(**kwargs)
