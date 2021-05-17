from CTFd.constants.config import (
    AccountVisibilityTypes,
    ChallengeVisibilityTypes,
    ConfigTypes,
    RegistrationVisibilityTypes,
    ExerciceVisibilityTypes, BadgeVisibilityTypes
)
from CTFd.utils import get_config
from CTFd.utils.user import authed, has_right


def challenges_visible():
    v = get_config(ConfigTypes.CHALLENGE_VISIBILITY)
    if v == ChallengeVisibilityTypes.PUBLIC:
        return True
    elif v == ChallengeVisibilityTypes.PRIVATE:
        return authed()
    elif v == ChallengeVisibilityTypes.ADMINS:
        return has_right("utils_config_visibility_challenges_visible")

def exercices_visible():
    v = get_config(ConfigTypes.EXERCICES_VISIBILITY)
    if v ==ExerciceVisibilityTypes.PUBLIC:
        return True
    elif v == ExerciceVisibilityTypes.PRIVATE:
        return authed()
    elif v == ExerciceVisibilityTypes.ADMINS:
        return is_admin()

def accounts_visible():
    v = get_config(ConfigTypes.ACCOUNT_VISIBILITY)
    if v == AccountVisibilityTypes.PUBLIC:
        return True
    elif v == AccountVisibilityTypes.PRIVATE:
        return authed()
    elif v == AccountVisibilityTypes.ADMINS:
        return has_right("utils_config_visibility_accounts_visible")


def registration_visible():
    v = get_config(ConfigTypes.REGISTRATION_VISIBILITY)
    if v == RegistrationVisibilityTypes.PUBLIC:
        return True
    elif v == RegistrationVisibilityTypes.PRIVATE:
        return False
    else:
        return False


def badges_visible():
    v = get_config(ConfigTypes.CHALLENGE_VISIBILITY)
    if v == BadgeVisibilityTypes.PUBLIC:
        return True
    elif v == BadgeVisibilityTypes.PRIVATE:
        return authed()
    elif v == BadgeVisibilityTypes.ADMINS:
        return is_admin()
