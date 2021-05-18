from CTFd.models import RoleRights, ma
from CTFd.utils import string_types


class RoleRightsSchema(ma.ModelSchema):
    class Meta:
        model = RoleRights
        include_fk = True
        dump_only = ("role_id", "right_id")

    views = {"admin": ["role_id", "right_id"], "user": ["role_id", "right_id"]}

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(RoleRightsSchema, self).__init__(*args, **kwargs)
