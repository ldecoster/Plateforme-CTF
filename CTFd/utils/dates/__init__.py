import datetime

from CTFd.utils import get_config


def ctf_paused():
    return bool(get_config("paused"))


def unix_time(dt):
    return int((dt - datetime.datetime(1970, 1, 1)).total_seconds())


def unix_time_millis(dt):
    return unix_time(dt) * 1000


def unix_time_to_utc(t):
    return datetime.datetime.utcfromtimestamp(t)


def isoformat(dt):
    return dt.isoformat() + "Z"
