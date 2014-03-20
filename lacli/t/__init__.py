from boto import set_stream_logger
from lacore.log import setupLogging
from lacore.date import epoch
from binascii import a2b_hex
from contextlib import contextmanager
from tempfile import mkdtemp
from shutil import rmtree


def setup():
    set_stream_logger('boto')
    setupLogging(2)


def makeprefs(factory=None):
    return {
        'api': {
            'user': 'foo',
            'pass': 'bar',
            'url': 'http://baz.com',
            'verify': True,
            'factory': factory
        },
        'upload': {
            'timeout': 1200,
            'bucket': 'lastage',
            'nprocs': None,
        },
        'command': {
            'debug': 0,
            'verbose': False,
            'batch': True,
            'unsafe': False,
            'srm': None
        },
        'gui': {
            'rememberme': False,
            'username': None,
            'password': None,
            'email': None
        }
    }

dummykey = a2b_hex(
    '824aed71bd74c656ed6bdaa19f2a338faedd824d5fd6e96e85b7fac5c6dabe18')

dummycapsule = {
    'title': 'foo',
    'id': 'bar',
    'size': 1230000,
    'remaining': 0,
    'expires': epoch(),
    'created': epoch()
}


@contextmanager
def _temp_home():
    d = mkdtemp()
    yield d
    rmtree(d)
