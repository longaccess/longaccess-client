from functools import update_wrapper, wraps


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
