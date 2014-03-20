from multiprocessing import current_process
from lacore.exceptions import BaseAppException


class CacheInitException(BaseAppException):
    msg = "Application cache not initialized correctly"


class ApiNoSessionError(BaseAppException):
    msg = "no session credentials provided."


class WorkerFailureError(BaseAppException):
    def __init__(self, *args, **kwargs):
        super(BaseAppException, self).__init__(self.msg, *args, **kwargs)
        self.msg = "worker '{}' failed".format(current_process())


class Timeout(BaseAppException):
    msg = "Timeout"


class PauseEvent(BaseAppException):
    msg = "Paused"


class CloudProviderUploadError(BaseAppException):
    msg = "cloud provider indicated an error while uploading"
