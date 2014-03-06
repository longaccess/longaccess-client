from lacli.exceptions import ApiAuthException, BaseAppException, PauseEvent
from lacli.server.interface.ClientInterface.ttypes import InvalidOperation
from lacli.server.interface.ClientInterface.ttypes import ErrorType
from lacli.log import getLogger
from twisted.python import log as twisted_log
from twisted.internet import defer
from functools import wraps
import errno


def log_hide(**kwargs):
    def decorator(f):
        setattr(f, '__hidden', kwargs)
        return f
    return decorator


def log_call(f):
    @wraps(f)
    @defer.inlineCallbacks
    def w(*args, **kwargs):
        hide = getattr(f, '__hidden', {})
        if len(args) > 0 and hasattr(args[0], "debug"):
            try:
                if int(args[0].debug) > 4:
                    hide = {}  # don't hide anything
            except:
                pass
        hidden = lambda k: k in hide and hide[k] is True
        maybe = lambda k, v: "<...>" if hidden(k) else v
        _as = maybe('_args', args[1:])
        _ks = {(k, maybe(k, v)) for k, v in kwargs.iteritems()}
        getLogger().debug("calling {} with {}, {}".format(f, _as, _ks))
        r = yield f(*args, **kwargs)
        getLogger().debug(
            "return value for {} is {}".format(f, maybe('_ret', r)))
        defer.returnValue(r)
    return w


def tthrow(f):
    """ Decorate a method to raise InvalidOperation instead
        of lacli exceptions
    """
    @wraps(f)
    @defer.inlineCallbacks
    def w(*args, **kwargs):
        r = None
        try:
            r = yield f(*args, **kwargs)
            defer.returnValue(r)
        except ApiAuthException as e:
            twisted_log.err(e)
            raise InvalidOperation(ErrorType.Authentication, e.msg)
        except NotImplementedError as e:
            getLogger().debug("{} is not implemented".format(f, r))
            raise InvalidOperation(ErrorType.NotImplemented, str(e))
        except OSError as e:
            getLogger().debug("{} threw exception".format(f), exc_info=True)
            if e.errno == errno.ENOENT:
                raise InvalidOperation(ErrorType.FileNotFound,
                                       "File not found",
                                       filename=e.filename)
            if e.errno == errno.EACCES:
                raise InvalidOperation(
                    ErrorType.Other, "Access denied or file in use")
            getLogger().debug("unknown exception", exc_info=True)
            raise InvalidOperation(ErrorType.Other, "Unknown error")
        except IOError as e:
            getLogger().debug("{} threw exception".format(f), exc_info=True)
            if e.errno == errno.ENOENT:
                raise InvalidOperation(ErrorType.FileNotFound,
                                       "File not found",
                                       filename=e.filename)
            if e.errno == errno.ENOSPC:
                raise InvalidOperation(ErrorType.Other,
                                       "No space left on device")
            getLogger().debug("unknown exception", exc_info=True)
            raise InvalidOperation(ErrorType.Other, "")
        except ValueError as e:
            getLogger().debug("{} threw exception".format(f), exc_info=True)
            raise InvalidOperation(ErrorType.Validation, str(e))
        except BaseAppException as e:
            getLogger().debug("application exception", exc_info=True)
            twisted_log.err(e)
            raise InvalidOperation(ErrorType.Other, str(e))
        except PauseEvent:
            pass
        except Exception as e:
            getLogger().debug("unknown exception", exc_info=True)
            twisted_log.err(e)
            raise InvalidOperation(ErrorType.Other, "Unknown error")
    return log_call(w)
