from wtforms import BooleanField, PasswordField, SelectField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.models import UserFieldEntries, UserFields
from CTFd.utils.countries import SELECT_COUNTRIES_LIST
from CTFd.utils.schools import SELECT_SCHOOLS_LIST
from CTFd.utils.specialisations import SELECT_SPECIALISATIONS_LIST
from CTFd.utils.cursus import SELECT_CURSUS_LIST
from CTFd.utils.user import has_right


def build_custom_user_fields(
    form_cls,
    include_entries=False,
    fields_kwargs=None,
    field_entries_kwargs=None,
    blacklisted_items=("website"),
):
    """
    Function used to reinject values back into forms for accessing by themes
    """
    if fields_kwargs is None:
        fields_kwargs = {}
    if field_entries_kwargs is None:
        field_entries_kwargs = {}

    fields = []
    new_fields = UserFields.query.filter_by(**fields_kwargs).all()
    user_fields = {}

    # Only include preexisting values if asked
    if include_entries is True:
        for f in UserFieldEntries.query.filter_by(**field_entries_kwargs).all():
            user_fields[f.field_id] = f.value

    for field in new_fields:
        if field.name.lower() in blacklisted_items:
            continue

        form_field = getattr(form_cls, f"fields[{field.id}]")

        # Add the field_type to the field so we know how to render it
        form_field.field_type = field.field_type

        # Only include preexisting values if asked
        if include_entries is True:
            initial = user_fields.get(field.id, "")
            form_field.data = initial
            if form_field.render_kw:
                form_field.render_kw["data-initial"] = initial
            else:
                form_field.render_kw = {"data-initial": initial}

        fields.append(form_field)
    return fields


def attach_custom_user_fields(form_cls, **kwargs):
    """
    Function used to attach form fields to wtforms.
    Not really a great solution but is approved by wtforms.

    https://wtforms.readthedocs.io/en/2.3.x/specific_problems/#dynamic-form-composition
    """
    new_fields = UserFields.query.filter_by(**kwargs).all()
    for field in new_fields:
        validators = []
        if field.required:
            validators.append(InputRequired())

        if field.field_type == "text":
            input_field = StringField(
                field.name, description=field.description, validators=validators
            )
        elif field.field_type == "boolean":
            input_field = BooleanField(
                field.name, description=field.description, validators=validators
            )

        setattr(form_cls, f"fields[{field.id}]", input_field)


class UserSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", "Name"),
            ("id", "ID"),
            ("email", "Email"),
            ("website", "Website"),
            ("ip", "IP Address"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")


class PublicUserSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", "Name"),
            ("website", "Website"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")


class UserBaseFormFull(BaseForm):
    name = StringField("User Name", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password")
    website = StringField("Website")
    country = SelectField("Country", choices=SELECT_COUNTRIES_LIST)
    school = SelectField("School", choices=SELECT_SCHOOLS_LIST)
    cursus = SelectField("Cursus", choices=SELECT_CURSUS_LIST)
    specialisation = SelectField("Specialisation", choices=SELECT_SPECIALISATIONS_LIST)
    type = SelectField("Type", choices=[
        ("user", "User"), ("contributor", "Contributor"), ("teacher", "Teacher"), ("admin", "Admin")
    ])
    verified = BooleanField("Verified")
    hidden = BooleanField("Hidden")
    banned = BooleanField("Banned")
    submit = SubmitField("Submit")


class UserBaseFormPartial(BaseForm):
    name = StringField("User Name", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password")
    website = StringField("Website")
    country = SelectField("Country", choices=SELECT_COUNTRIES_LIST)
    school = SelectField("School", choices=SELECT_SCHOOLS_LIST)
    cursus = SelectField("Cursus", choices=SELECT_CURSUS_LIST)
    specialisation = SelectField("Specialisation", choices=SELECT_SPECIALISATIONS_LIST)
    type = SelectField("Type", choices=[("user", "User"), ("contributor", "Contributor")])
    verified = BooleanField("Verified")
    hidden = BooleanField("Hidden")
    banned = BooleanField("Banned")
    submit = SubmitField("Submit")


def UserEditForm(*args, **kwargs):
    if has_right("forms_user_edit_form_full"):
        class _UserEditForm(UserBaseFormFull):
            pass

            @property
            def extra(self):
                return build_custom_user_fields(
                    self,
                    include_entries=True,
                    fields_kwargs=None,
                    field_entries_kwargs={"user_id": self.obj.id},
                )

            def __init__(self, *args, **kwargs):
                """
                Custom init to persist the obj parameter to the rest of the form
                """
                super().__init__(*args, **kwargs)
                obj = kwargs.get("obj")
                if obj:
                    self.obj = obj
    elif has_right("forms_user_edit_form_partial"):
        class _UserEditForm(UserBaseFormPartial):
            pass

            @property
            def extra(self):
                return build_custom_user_fields(
                    self,
                    include_entries=True,
                    fields_kwargs=None,
                    field_entries_kwargs={"user_id": self.obj.id},
                )

            def __init__(self, *args, **kwargs):
                """
                Custom init to persist the obj parameter to the rest of the form
                """
                super().__init__(*args, **kwargs)
                obj = kwargs.get("obj")
                if obj:
                    self.obj = obj

    attach_custom_user_fields(_UserEditForm)

    return _UserEditForm(*args, **kwargs)


def UserCreateForm(*args, **kwargs):
    if has_right("forms_user_create_form_full"):
        class _UserCreateForm(UserBaseFormFull):
            notify = BooleanField("Email account credentials to user", default=True)

            @property
            def extra(self):
                return build_custom_user_fields(self, include_entries=False)
    elif has_right("forms_user_create_form_partial"):
        class _UserCreateForm(UserBaseFormPartial):
            notify = BooleanField("Email account credentials to user", default=True)

            @property
            def extra(self):
                return build_custom_user_fields(self, include_entries=False)

    attach_custom_user_fields(_UserCreateForm)

    return _UserCreateForm(*args, **kwargs)
