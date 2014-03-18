import shlex

from lacli.log import getLogger
from lacli.enc import get_unicode
from lacli.exceptions import CacheInitException
from functools import wraps
from docopt import docopt, DocoptExit


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
