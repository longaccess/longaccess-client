import shlex
import sys

from lacli.enc import get_unicode
from lacli.log import getLogger
from twisted.internet import defer
from twisted.python.failure import Failure
from twisted.internet import reactor
from docopt import docopt, DocoptExit
from functools import update_wrapper, wraps, partial
from requests.exceptions import ConnectionError, HTTPError
from lacli.exceptions import (ApiErrorException, ApiAuthException, CacheInitException,
                              ApiUnavailableException, ApiNoSessionError, BaseAppException)
from crochet import setup, run_in_reactor, TimeoutError

def expand_args(f):
    @wraps(f)
    def wrap(args=[], kwargs={}):
        return f(*args, **kwargs)
    return wrap


class deferred_property(object):
    def __init__(self, f):
        self.f = defer.inlineCallbacks(f)
        update_wrapper(self, self.f)

    def update(self, obj, name, value):
        if isinstance(value, Failure):
            del obj.__dict__[name]
        else:
            obj.__dict__[name]=value
        return value

    def __get__(self, obj, cls):
        if obj is None:
            return self
        name = self.f.__name__
        if name not in obj.__dict__:
            obj.__dict__[name] = self.f(obj)
            obj.__dict__[name].addBoth(
                partial(self.update, obj, name))
        return obj.__dict__[name]

    def __set__(self, obj, value):
        obj.__dict__[self.f.__name__] = value


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
                        if types[kw] == unicode:
                            kwargs[kw] = get_unicode(val)
                        else:
                            kwargs[kw] = types[kw](val)
            except ValueError as e:
                print "error: invalid value:", e
                print func.__doc__
                return
            except DocoptExit as e:
                print e
                return
            try:
                func(self, **kwargs)
            except CacheInitException as e:
                getLogger().debug("Cache not initialized", exc_info=True)
                print "Could not initialize cache"
                return
        return wrap
    return decorate


def block(f):
    """ Decorate a method to block in crochet reactor
    """
    fblocking = run_in_reactor(f)
    @wraps(f)
    def wrap(*args, **kwargs):
        if not reactor.running:
            setup()
        result = fblocking(*args, **kwargs)
        try:
            return result.wait()
        except TimeoutError:
            result.cancel()
            raise
    return wrap


class login_async(object):
    def __init__(self, f, obj=None):
        self.f = f
        self.obj = obj
        update_wrapper(self, self.f)

    def __get__(self, obj, cls):
        return wraps(self.f)(login(self.f, obj))

    def dologin(self, prefs):
        return self.obj.registry.cmd.login.login_async(
            prefs.get('user'), prefs.get('pass'))

    @defer.inlineCallbacks
    def loginfirst(self, prefs, *args, **kwargs):
        yield self.dologin(prefs)
        r = yield self.f(self.obj, *args, **kwargs)
        defer.returnValue(r)

    def __call__(self, *args, **kwargs):
        if len(args) > 0:
            if self.obj is None:
                self.obj = args[0]
                args = args[1:]
            elif self.obj == args[0]:
                args = args[1:]

        prefs = None
        if self.obj.registry.session:
            prefs = self.obj.registry.session.prefs
        if not prefs:
            prefs = self.obj.registry.init_prefs()

        if not self.obj.session or self.obj.registry.cmd.login.email is None:
            return self.loginfirst(prefs, *args, **kwargs)
        return self.f(self.obj, *args, **kwargs)


class login(login_async):
    def __init__(self, *args, **kwargs):
        super(login, self).__init__(*args, **kwargs)
    
    def dologin(self, prefs):
        if self.obj.batch:
            self.obj.registry.cmd.login.login_batch(
                prefs.get('user'), prefs.get('pass'))
        else:
            cmdline = [prefs[a] for a in ['user', 'pass']
                       if prefs.get(a)]
            self.obj.registry.cmd.username = prefs['user']
            self.obj.registry.cmd.password = prefs['pass']
            self.obj.registry.cmd.do_login(" ".join(cmdline))

    def loginfirst(self, *args, **kwargs):
       return super(login, self).loginfirst(*args, **kwargs)
