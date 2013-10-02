from boto import set_stream_logger
from lacli.log import setupLogging


def setup():
    set_stream_logger('boto')
    setupLogging(2)


def makeprefs():
    return {
        'api': {
            'user': 'foo',
            'pass': 'bar',
            'url': 'http://baz.com',
        },
        'upload': {
            'timeout': 1200,
            'bucket': 'lastage',
            'nprocs': None,
        },
        'command': {
            'debug': 0
        },
    }
