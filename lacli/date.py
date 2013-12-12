import dateutil.parser
import dateutil.tz
from dateutil.relativedelta import relativedelta as date_delta
from datetime import datetime


def parse_timestamp(string):
    if not string or isinstance(string, datetime):
        return string
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


def later(d, **args):
    return d + date_delta(**args)
