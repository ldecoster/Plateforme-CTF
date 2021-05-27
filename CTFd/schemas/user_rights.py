from CTFd.models import UserRights, ma
from CTFd.utils import string_types


class UserRightsSchema(ma.ModelSchema):
    class Meta:
        model = UserRights
        include_fk = True
        dump_only = ("user_id", "right_id")

    views = {"admin": ["user_id", "right_id"], "user": ["user_id", "right_id"]}

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(UserRightsSchema, self).__init__(*args, **kwargs)
