import datetime


def get_UTC_timestamp():
    return datetime.datetime.now(datetime.timezone.utc).timestamp()