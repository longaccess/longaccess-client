class BaseApiException(Exception):
    msg = "error"

    def __init__(self, *args, **kwargs):
        super(BaseApiException, self).__init__(self.msg, *args, **kwargs)


class ApiErrorException(BaseApiException):
    msg = "server not found"


class ApiUnavailableException(BaseApiException):
    msg = "the server couldn't fulfill your request"


class ApiAuthException(BaseApiException):
    msg = "authentication failed"
