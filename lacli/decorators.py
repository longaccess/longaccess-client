import shlex

from docopt import docopt, DocoptExit
from functools import update_wrapper, wraps
from requests.exceptions import ConnectionError, HTTPError
from lacli.exceptions import (ApiErrorException, ApiAuthException,
                              ApiUnavailableException, ApiNoSessionError)


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
                raise ApiAuthException(e)
            else:
                raise ApiErrorException(e)
        except ApiNoSessionError:
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


def command(**types):
    """ Decorator to parse command options with docopt and
        validate the types.
    """
    def decorate(func):
        @wraps(func)
        def wrap(self, line):
            kwargs = {}
            try:
                opts = docopt(func.__doc__, shlex.split(line))
                for opt, val in opts.iteritems():
                    kw = opt.strip('<>')
                    if val and kw in types:
                        kwargs[kw] = types[kw](val)
            except ValueError as e:
                print "error: invalid value:", shlex.split(e.message).pop()
                print func.__doc__
                return
            except DocoptExit as e:
                print e
                return
            func(self, **kwargs)
        return wrap
    return decorate


class login(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, cls):
        prefs = obj.registry.session.prefs

        @wraps(self.f)
        def wrap(*args, **kwargs):
            if not prefs.get('pass'):
                obj.registry.cmd.do_login(
                    prefs.get('user') or '')
            if obj.registry.prefs['api'].get('user'):
                self.f(obj, *args, **kwargs)
        return wrap
