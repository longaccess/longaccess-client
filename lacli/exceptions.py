class BaseAppException(Exception):
    msg = "error"

    def __init__(self, exc, *args, **kwargs):
        super(BaseAppException, self).__init__(self.msg, *args, **kwargs)
        self.exc = exc

    def __str__(self):
        return self.msg


class ApiErrorException(BaseAppException):
    msg = "the server couldn't fulfill your request"


class ApiUnavailableException(BaseAppException):
    msg = "server not found"


class ApiAuthException(BaseAppException):
    msg = "authentication failed"
