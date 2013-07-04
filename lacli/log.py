import logging
import logutils.queue
from contextlib import contextmanager
from multiprocessing import Queue

simplefmt='%(name)-15s %(levelname)-8s %(processName)-10s %(message)s'

def setupLogging(level,logfile=None, queue=False):
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
                        'level': 'DEBUG' if level else 'INFO',
                        'formatter': 'simple',
                    },
                },
                'root': {
                    'level': 'DEBUG' if level else 'INFO',
                    'handlers': ['console'],
                },
            })
    else:
        raise NotImplementedError("Log to file is not implemented yet")

class queueHandler(object):
     def __init__(self, logger='queue'):
        self.logger=logging.getLogger(logger)
     def handle(self, msg):
         self.logger.handle(msg)

@contextmanager
def queueOpened():
    q=Queue()
    listener = logutils.queue.QueueListener(q, queueHandler('lacli'))
    listener.start()
    yield q
    listener.stop()

def logToQueue(level, queue):
    logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
            'handlers': {
                'queue': {
                    'class': 'logutils.queue.QueueHandler',
                    'queue': queue,
                },
            },
            'root': {
                'level': 'DEBUG' if level else 'INFO',
                'handlers': ['queue']
            },
        })


def getLogger(logger='lacli'):
    return logging.getLogger(logger)
