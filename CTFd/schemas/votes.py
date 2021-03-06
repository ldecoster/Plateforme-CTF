from CTFd.models import Votes, ma
from CTFd.utils import string_types


class VoteSchema(ma.ModelSchema):
    class Meta:
        model = Votes
        include_fk = True
        dump_only = ("id",)

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(VoteSchema, self).__init__(*args, **kwargs)
