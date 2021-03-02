from CTFd.models import Roles, ma
from CTFd.utils import string_types


class RoleSchema(ma.ModelSchema):
    class Meta:
        model = Roles
        include_fk = True
        dump_only = ("id", "name")

    views = {
        "admin": [
            "id",
            "name",
        ],
        "user": [
            "id",
            "name",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(RoleSchema, self).__init__(*args, **kwargs)
