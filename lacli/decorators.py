from functools import update_wrapper, wraps
from requests.exceptions import ConnectionError, HTTPError
from lacli.exceptions import ApiErrorException, ApiUnavailableException


class cached_property(object):
    val = None

    def __init__(self, f):
        self.f = f
        update_wrapper(self, self.f)

    def __get__(self, obj, cls):
        if self.val is None:
            self.val = self.f(obj)
        return self.val


def with_api_response(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            r = f(*args, **kwargs)
            r.raise_for_status()
            return r.json()
        except ConnectionError as e:
            raise ApiUnavailableException(e)
        except HTTPError as e:
            if e.response.status_code == 404:
                raise ApiUnavailableException(e)
            else:
                raise ApiErrorException(e)
        except Exception as e:
            raise ApiErrorException(e)
    return wrap
