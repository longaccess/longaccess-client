from lacli.exceptions import ApiAuthException
from lacli.server.interface.ClientInterface.ttypes import InvalidOperation
from lacli.server.interface.ClientInterface.ttypes import ErrorType
from lacli.log import getLogger
from twisted.python import log as twisted_log
from functools import wraps


def tthrow(f):
    """ Decorate a method to raise InvalidOperation instead
        of lacli exceptions
    """

    @wraps(f)
    def w(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ApiAuthException as e:
            raise InvalidOperation(ErrorType.Authentication, e.msg)
        except NotImplementedError as e:
            raise InvalidOperation(ErrorType.NotImplemented, str(e))
        except Exception as e:
            getLogger().debug("unhandled exception",
                              exc_info=True)
            twisted_log.err(e)
            raise InvalidOperation(ErrorType.Other, "Unknown error")
    return w
