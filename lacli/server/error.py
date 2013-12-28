from lacli.exceptions import ApiAuthException
from lacli.server.interface.ClientInterface.ttypes import InvalidOperation
from lacli.server.interface.ClientInterface.ttypes import ErrorType
from lacli.log import getLogger
from twisted.python import log as twisted_log
from twisted.python import failure
from twisted.internet import defer
from functools import wraps
import errno


def tthrow(f):
    """ Decorate a method to raise InvalidOperation instead
        of lacli exceptions
    """
    @wraps(f)
    @defer.inlineCallbacks
    def w(*args, **kwargs):
        r = None
        try:
            getLogger().debug("calling {}".format(f))
            r = yield f(*args, **kwargs)
            getLogger().debug("return value for {} is {}".format(f, r))
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
                raise InvalidOperation(ErrorType.Other, "Access denied or file in use")
            getLogger().debug("unknown exception", exc_info=True)
            raise InvalidOperation(ErrorType.Other, "Unknown error")
        except IOError as e:
            getLogger().debug("{} threw exception".format(f), exc_info=True)
            if e.errno == errno.ENOENT:
                raise InvalidOperation(ErrorType.FileNotFound,
                                       "File not found",
                                       filename=e.filename)
            getLogger().debug("unknown exception", exc_info=True)
            raise InvalidOperation(ErrorType.Other, "Unknown error")
        except ValueError as e:
            getLogger().debug("{} threw exception".format(f), exc_info=True)
            raise InvalidOperation(ErrorType.Validation, str(e))
        except Exception as e:
            getLogger().debug("unknown exception", exc_info=True)
            twisted_log.err(e)
            raise InvalidOperation(ErrorType.Other, "Unknown error")
    return w
