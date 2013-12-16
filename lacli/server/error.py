from lacli.exceptions import ApiAuthException
from lacli.server.interface.ClientInterface.ttypes import InvalidOperation
from lacli.server.interface.ClientInterface.ttypes import ErrorType
from functools import wraps


def tthrow(f):
    """ Decorate a method to raise InvalidOperation instead
        of lacli exceptions
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ApiAuthException as e:
            raise InvalidOperation(ErrorType.Authentication, e.msg)
        except NotImplementedError as e:
            raise InvalidOperation(ErrorType.NotImplemented, str(e))
        except Exception as e:
            raise InvalidOperation(ErrorType.Other, "Unknown error")

    return wrap
