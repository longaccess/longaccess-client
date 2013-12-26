from lacli.exceptions import ApiAuthException
from lacli.server.interface.ClientInterface.ttypes import InvalidOperation
from lacli.server.interface.ClientInterface.ttypes import ErrorType
from lacli.log import getLogger
from twisted.python import log as twisted_log
from twisted.python import failure
from twisted.internet.defer import Deferred
from functools import wraps
import errno


def makeInvalidOperation(error):
    try:
        error.raiseException()
    except ApiAuthException as e:
        raise InvalidOperation(ErrorType.Authentication, e.msg)
    except NotImplementedError as e:
        raise InvalidOperation(ErrorType.NotImplemented, str(e))
    except OSError as e:
        if e.errno == errno.ENOENT:
            raise InvalidOperation(ErrorType.FileNotFound,
                                   filename=e.filename)
    except ValueError as e:
        raise InvalidOperation(ErrorType.Validation, str(e))
    except Exception as e:
        getLogger().debug("unhandled exception",
                          exc_info=True)
        twisted_log.err(e)
        raise InvalidOperation(ErrorType.Other, "Unknown error")


def tthrow(f):
    """ Decorate a method to raise InvalidOperation instead
        of lacli exceptions
    """
    @wraps(f)
    def w(*args, **kwargs):
        r = None
        try:
            r = f(*args, **kwargs)
            
            if isinstance(r, Deferred):
                r.addErrback(makeInvalidOperation)
            return r
        except Exception as e:
            if isinstance(r, Deferred):
                r.cancel()
            return makeInvalidOperation(failure.Failure(e))
    return w
