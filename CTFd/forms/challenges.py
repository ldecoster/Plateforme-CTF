from wtforms import MultipleFileField, SelectField, StringField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField

class ChallengesFilterForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", "Name"),
            ("author", "Author"),
            ("tags", "Tag"),
            ("type", "Type"),
            ("sucess", "Challenge Succeded"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")

class ChallengeSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", "Name"),
            ("id", "ID"),
            ("tags", "Tag"),
            ("type", "Type"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")


class ChallengeFilesUploadForm(BaseForm):
    file = MultipleFileField(
        "Upload Files",
        description="Attach multiple files using Control+Click or Cmd+Click.",
        validators=[InputRequired()],
    )
    submit = SubmitField("Upload")