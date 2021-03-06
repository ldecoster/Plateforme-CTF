from wtforms import BooleanField, SelectField, StringField, TextAreaField
from wtforms.fields.html5 import URLField

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.models import db


class ResetInstanceForm(BaseForm):
    accounts = BooleanField(
        "Accounts",
        description="Deletes all user accounts and their associated information",
    )
    submissions = BooleanField(
        "Submissions",
        description="Deletes all records that accounts took an action",
    )
    challenges = BooleanField(
        "Challenges", description="Deletes all challenges and associated data"
    )
    pages = BooleanField(
        "Pages", description="Deletes all pages and their associated files"
    )
    notifications = BooleanField(
        "Notifications", description="Deletes all notifications"
    )
    submit = SubmitField("Reset CTF")


class AccountSettingsForm(BaseForm):
    domain_whitelist = StringField(
        "Account Email Whitelist",
        description="Comma-seperated email domains which users can register under (e.g. ctfd.io, gmail.com, yahoo.com)",
    )
    verify_emails = SelectField(
        "Verify Emails",
        description="Control whether users must confirm their email addresses before playing",
        choices=[("true", "Enabled"), ("false", "Disabled")],
        default="false",
    )
    name_changes = SelectField(
        "Name Changes",
        description="Control whether users can change their names",
        choices=[("true", "Enabled"), ("false", "Disabled")],
        default="true",
    )

    submit = SubmitField("Update")


class ExportCSVForm(BaseForm):
    table = SelectField(
        "Database Table",
        choices=list(
            zip(sorted(db.metadata.tables.keys()), sorted(db.metadata.tables.keys()))
        ),
    )
    submit = SubmitField("Download CSV")


class LegalSettingsForm(BaseForm):
    tos_url = URLField(
        "Terms of Service URL",
        description="External URL to a Terms of Service document hosted elsewhere",
    )
    tos_text = TextAreaField(
        "Terms of Service", description="Text shown on the Terms of Service page",
    )
    privacy_url = URLField(
        "Privacy Policy URL",
        description="External URL to a Privacy Policy document hosted elsewhere",
    )
    privacy_text = TextAreaField(
        "Privacy Policy", description="Text shown on the Privacy Policy page",
    )
    submit = SubmitField("Update")
