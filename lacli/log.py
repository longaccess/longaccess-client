import logging
import logutils.queue
from contextlib import contextmanager
from multiprocessing import Queue
from boto import config as boto_config

simplefmt='%(name)-15s %(levelname)-8s %(processName)-10s %(message)s'

def setupLogging(level,logfile=None, queue=False):
    # this overrides any user debug setting in the boto configuration
    if not boto_config.has_section('Boto'):
        boto_config.add_section('Boto')

    if level==0:
        level='WARN'
        boto_config.set('Boto', 'debug', '0')
    elif level==1:
        level='INFO'
        boto_config.set('Boto', 'debug', '0')
    elif level==2:
        level='DEBUG'
        boto_config.set('Boto', 'debug', '1')
    else:
        level='DEBUG'
        boto_config.set('Boto', 'debug', '2')

    if logfile is None:
        logging.config.dictConfig({
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
                    },
                },
                'loggers': {
                    'boto': {
                        'handlers': ['console'],
                    },
                    'lacli': {
                        'handlers': ['console']
                    },
                    'multiprocessing': {
                        'handlers': ['console']
                    },
                },
                'root': {
                    'level': level,
                    'handlers': ['console'],
                },
            })
    else:
        raise NotImplementedError("Log to file is not implemented yet")

class logHandler(object):
    def __init__(self, logger='lacli'):
        self.logger=getLogger(logger)
    def handle(self, msg):
        self.logger.handle(msg)

@contextmanager
def queueOpened(handler):
    q=Queue()
    listener = logutils.queue.QueueListener(q, handler)
    listener.start()
    yield q
    listener.stop()

def logToQueue(queue):
    logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
            'handlers': {
                'queue': {
                    'class': 'logutils.queue.QueueHandler',
                    'queue': queue,
                },
            },
            'loggers': {
                'boto': {
                    'handlers': ['queue']
                },
                'lacli': {
                    'handlers': ['queue']
                },
            },
            'root': {
                'level': 'DEBUG',
                'handlers': ['queue']
            },
        })


def getLogger(logger='lacli'):
    return logging.getLogger(logger)
