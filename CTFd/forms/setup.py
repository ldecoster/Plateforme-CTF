from wtforms import (
    HiddenField,
    PasswordField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.utils.config import get_themes


class SetupForm(BaseForm):
    ctf_name = StringField(
        "Event Name", description="The name of your CTF event/workshop"
    )
    ctf_description = TextAreaField(
        "Event Description", description="Description for the CTF"
    )

    name = StringField(
        "Admin Username",
        description="Your username for the administration account",
        validators=[InputRequired()],
    )
    email = EmailField(
        "Admin Email",
        description="Your email address for the administration account",
        validators=[InputRequired()],
    )
    password = PasswordField(
        "Admin Password",
        description="Your password for the administration account",
        validators=[InputRequired()],
    )

    ctf_theme = SelectField(
        "Theme",
        description="CTFd Theme to use",
        choices=list(zip(get_themes(), get_themes())),
        default="core",
        validators=[InputRequired()],
    )
    theme_color = HiddenField(
        "Theme Color",
        description="Color used by theme to control aesthetics. Requires theme support. Optional.",
    )

    submit = SubmitField("Finish")
