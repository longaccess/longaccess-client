import logging
from boto import config as boto_config
from twisted.internet.defer import setDebugging as debugTwisted
from twisted.python import log as twisted_log
from contextlib import contextmanager


simplefmt = '%(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
logging.basicConfig(format=simplefmt)


def setupLogging(level, logfile=None, queue=False):
    # this overrides any user debug setting in the boto configuration
    if not boto_config.has_section('Boto'):
        boto_config.add_section('Boto')

    import httplib
    httplib.HTTPConnection.debuglevel = level

    if level == 0:
        level = 'WARN'
        boto_config.set('Boto', 'debug', '0')
    elif level == 1:
        level = 'INFO'
        boto_config.set('Boto', 'debug', '0')
    elif level == 2:
        level = 'DEBUG'
        boto_config.set('Boto', 'debug', '1')
    else:
        level = 'DEBUG'
        boto_config.set('Boto', 'debug', '2')
        debugTwisted(True)

    logconf = {
        'version': 1,
        'formatters': {
            'simple': {
                'class': 'logging.Formatter',
                'format': simplefmt,
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'simple',
            }
        },
        'loggers': {
            'boto': {
                'handlers': ['console'],
                'propagate': True
            },
            'lacli': {
                'handlers': ['console'],
                'propagate': True
            },
            'multiprocessing': {
                'handlers': ['console'],
                'propagate': True
            },
            'requests.packages.urllib3': {
                'handlers': ['console'],
                'propagate': True
            },
            'twisted': {
                'handlers': ['console'],
                'propagate': True
            }
        },
        'root': {'level': level}
    }

    logging.config.dictConfig(logconf)

    return log_open(logfile)


@contextmanager
def log_open(log):
    logfile = None
    if log is not None:
        try:
            logfile = open(log, 'w+')
            handler = logging.StreamHandler(logfile)
            handler.setFormatter(logging.Formatter(simplefmt))
            logging.getLogger('').addHandler(handler)
        except Exception:
            getLogger().debug("couldn't open log", exc_info=True)

    observer = twisted_log.PythonLoggingObserver()
    observer.start()

    yield None

    observer.stop()

    if logfile is not None:
        logfile.close()


def getLogger(logger='lacli'):
    return logging.getLogger(logger)
