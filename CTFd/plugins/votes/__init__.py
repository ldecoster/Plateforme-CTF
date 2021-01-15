from CTFd.plugins import register_plugin_assets_directory


class VoteException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class BaseVote(object):
    name = None
    templates = {}


class CTFdVote(BaseVote):
    name = "default"
    templates = {  # Nunjucks templates used for key editing & viewing
        "create": "/plugins/votes/assets/create.html",
        "update": "/plugins/votes/assets/edit.html",
    }


VOTE_CLASSES = {"default": CTFdVote}


def get_vote_class(class_id):
    cls = VOTE_CLASSES.get(class_id)
    if cls is None:
        raise KeyError
    return cls


def load(app):
    register_plugin_assets_directory(app, base_path="/plugins/votes/assets/")
