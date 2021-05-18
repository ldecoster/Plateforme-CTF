import re
from urllib.parse import urljoin, urlparse

from flask import request
from marshmallow import ValidationError

from CTFd.models import Users
from CTFd.utils.countries import lookup_country_code
from CTFd.utils.schools import lookup_school_code
from CTFd.utils.cursus import lookup_cursus_code
from CTFd.utils.specialisations import lookup_specialisation_code
from CTFd.utils.user import get_current_user, has_right

EMAIL_REGEX = r"(^[^@\s]+@[^@\s]+\.[^@\s]+$)"


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def validate_url(url):
    return urlparse(url).scheme.startswith("http")


def validate_email(email):
    return bool(re.match(EMAIL_REGEX, email))


def unique_email(email, model=Users):
    obj = model.query.filter_by(email=email).first()
    if has_right("utils_validators_unique_email"):
        if obj:
            raise ValidationError("Email address has already been used")
    if obj and obj.id != get_current_user().id:
        raise ValidationError("Email address has already been used")


def validate_country_code(country_code):
    if country_code.strip() == "":
        return
    if lookup_country_code(country_code) is None:
        raise ValidationError("Invalid Country")


def validate_school_code(school_code):
    if school_code.strip() == "":
        return
    if lookup_school_code(school_code) is None:
        raise ValidationError("Invalid school")


def validate_cursus_code(cursus_code):
    if cursus_code.strip() == "":
        return
    if lookup_cursus_code(cursus_code) is None:
        raise ValidationError("Invalid cursus")


def validate_specialisation_code(specialisation_code):
    if specialisation_code.strip() == "":
        return
    if lookup_specialisation_code(specialisation_code) is None:
        raise ValidationError("Invalid specialisation")
