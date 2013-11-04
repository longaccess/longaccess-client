from multiprocessing import current_process


class BaseAppException(Exception):
    msg = "error"

    def __init__(self, exc=None, *args, **kwargs):
        super(BaseAppException, self).__init__(self.msg, *args, **kwargs)
        self.exc = exc

    def __str__(self):
        return self.msg


class ApiNoSessionError(BaseAppException):
    msg = "no session credentials provided."


class ApiErrorException(BaseAppException):
    msg = "the server couldn't fulfill your request"


class ApiUnavailableException(BaseAppException):
    msg = "resource not found"


class ApiAuthException(BaseAppException):
    msg = "authentication failed"


class UploadEmptyError(BaseAppException):
    msg = "upload failed"


class WorkerFailureError(BaseAppException):
    def __init__(self, *args, **kwargs):
        super(BaseAppException, self).__init__(self.msg, *args, **kwargs)
        self.msg = "worker '{}' failed".format(current_process())


class InvalidArchiveError(BaseAppException):
    msg = "invalid archive"


class DecryptionError(BaseAppException):
    msg = "Error decrypting file"

    def __init__(self, reason=None):
        super(DecryptionError, self).__init__()
        self.reason = reason
