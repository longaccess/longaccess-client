from twisted.python.failure import Failure
from twisted.internet import reactor, defer
from crochet import setup, run_in_reactor, TimeoutError
from functools import update_wrapper, wraps, partial


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


class deferred_property(object):
    def __init__(self, f):
        self.f = defer.inlineCallbacks(f)
        update_wrapper(self, self.f)

    def update(self, obj, name, value):
        if isinstance(value, Failure):
            del obj.__dict__[name]
        else:
            obj.__dict__[name] = value
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
