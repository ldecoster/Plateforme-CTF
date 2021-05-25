from CTFd.models import Badges, ma
from CTFd.utils import string_types


class BadgeSchema(ma.ModelSchema):
    class Meta:
        model = Badges
        include_fk = True
        dump_only = ("id", "title", "content")

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(BadgeSchema, self).__init__(*args, **kwargs)
