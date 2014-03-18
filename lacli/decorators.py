from functools import update_wrapper, wraps
from requests.exceptions import ConnectionError, HTTPError
from lacli.exceptions import (ApiErrorException, ApiAuthException,
                              ApiUnavailableException,
                              ApiNoSessionError, BaseAppException)


def expand_args(f):
    @wraps(f)
    def wrap(args=[], kwargs={}):
        return f(*args, **kwargs)
    return wrap


class cached_property(object):
    val = None

    def __init__(self, f):
        self.f = f
        update_wrapper(self, self.f)

    def __get__(self, obj, cls):
        if obj is None:
            return self
        if not self.f.__name__ in obj.__dict__:
            obj.__dict__[self.f.__name__] = self.f(obj)
        return obj.__dict__[self.f.__name__]

    def __set__(self, obj, value):
        obj.__dict__[self.f.__name__] = value


def with_api_response(f):
    """ Decorate a method to capture API related errors
    """
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
            elif e.response.status_code == 401:
                raise ApiAuthException(exc=e)
            else:
                raise ApiErrorException(e)
        except ApiNoSessionError:
            raise
        except BaseAppException:
            raise
        except Exception as e:
            raise ApiErrorException(e)
    return wrap


def contains(cls):
    def decorator(func):
        @wraps(func)
        def patched(*args, **kwargs):
            return cls(func(*args, **kwargs))
        return patched
    return decorator


def coroutine(func):
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        g.next()
        return g
    return start

# vim: et:sw=4:ts=4
