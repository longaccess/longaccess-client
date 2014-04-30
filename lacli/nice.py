import psutil
from functools import wraps


def with_low_priority(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        p = psutil.Process()
        op = p.nice()
        try:
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        except:
            p.nice(20)
        r = f(*args, **kwargs)
        try:
            p.nice(op)  # This will fail in POSIX systems
        except psutil.AccessDenied:
            pass
        return r
    return wrapper
