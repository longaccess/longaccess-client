from boto import set_stream_logger
from lacli.log import setupLogging
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


@contextmanager
def _temp_home():
    d = mkdtemp()
    yield d
    rmtree(d)
