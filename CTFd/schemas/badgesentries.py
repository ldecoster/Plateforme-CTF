from CTFd.models import BadgesEntries, ma
from CTFd.utils import string_types


class BadgesEntriesSchema(ma.ModelSchema):
    class Meta:
        model = BadgesEntries
        include_fk = True
        dump_only = ("id", "date")

    views = {
        "admin": [
            "category",
            "user_id",
            "name",
            "description",
            "user",
            ##"date",
            "requirements",
            "id",
            "icon",
        ],
        "user": [
            "category",
            "user_id",
            "name",
            "description",
            "user",
            ##"date",
            "id",
            "icon",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(BadgesEntriesSchema, self).__init__(*args, **kwargs)
