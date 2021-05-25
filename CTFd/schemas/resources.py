from CTFd.models import Resources, ma
from CTFd.utils import string_types


class ResourceSchema(ma.ModelSchema):
    class Meta:
        model = Resources
        include_fk = True
        dump_only = ("id", "type", "html")

    views = {
        "admin": [
            "id",
            "type",
            "challenge",
            "challenge_id",
            "content",
            "html",
        ],
        "user": [
            "id",
            "type",
            "challenge",
            "challenge_id",
            "content",
            "html",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(ResourceSchema, self).__init__(*args, **kwargs)
