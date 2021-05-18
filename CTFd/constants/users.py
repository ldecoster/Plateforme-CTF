from collections import namedtuple

UserAttrs = namedtuple(
    "UserAttrs",
    [
        "id",
        "name",
        "email",
        "type",
        "secret",
        "website",
        "country",
        "school",
        "cursus",
        "specialisation",
        "bracket",
        "hidden",
        "banned",
        "verified",
        "created",
    ],
)


class _UserAttrsWrapper:
    def __getattr__(self, attr):
        from CTFd.utils.user import get_current_user_attrs

        attrs = get_current_user_attrs()
        return getattr(attrs, attr, None)


User = _UserAttrsWrapper()
