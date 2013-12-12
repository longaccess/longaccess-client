import dateutil.parser
import dateutil.tz
from datetime import datetime


def parse_timestamp(string):
    try:
        d = dateutil.parser.parse(string)
        if d.utcoffset() is not None:
            return d.astimezone(dateutil.tz.tzutc())
        return d
    except TypeError:
        raise ValueError("invalid time stamp: " + str(string))


def remaining_time(d):
    if d.utcoffset() is not None:
        return d - datetime.now(dateutil.tz.tzutc())
    return d - datetime.utcnow()


def today():
    return datetime.now(dateutil.tz.tzutc()).replace(microsecond=0)
