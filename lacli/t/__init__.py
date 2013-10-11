from boto import set_stream_logger
from lacli.log import setupLogging
from binascii import a2b_hex


def setup():
    set_stream_logger('boto')
    setupLogging(2)


def makeprefs():
    return {
        'api': {
            'user': 'foo',
            'pass': 'bar',
            'url': 'http://baz.com',
            'verify': True
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

dummykey = a2b_hex(
    '824aed71bd74c656ed6bdaa19f2a338faedd824d5fd6e96e85b7fac5c6dabe18')

dummyurl = 'http://download.longaccess.com/x0fs8907494875'
