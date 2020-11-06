from CTFd.models import TagChallenge, ma
from CTFd.utils import string_types

class TagChallengeSchema(ma.ModelSchema):
    class Meta:
        model = TagChallenge
        include_fk = True
        dump_only=("tagId")

    views = {"admin": ["tagId","challengeId"],"user":["tagId","challengeId"]}

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(TagChallengeSchema, self).__init__(*args, **kwargs)
