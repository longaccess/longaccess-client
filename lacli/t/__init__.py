from boto import set_stream_logger
from lacli.log import setupLogging
from lacore.date import epoch
from binascii import a2b_hex
from contextlib import contextmanager
from tempfile import mkdtemp
from shutil import rmtree
from logging import Handler as LogHandler


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
    'created': epoch(),
    'resource_uri': '/foo/bar'
}

dummyarchive = {
    'capsule': '/foo/bar',
    'description': "dummy capsule",
    'resource_uri': '/foo/baz',
    'title': 'faz',
    'key': 'baz',
    'size': 1230000,
    'expires': epoch(),
    'created': epoch()
}


@contextmanager
def _temp_home():
    d = mkdtemp()
    yield d
    rmtree(d)


class MockLoggingHandler(LogHandler):
    """Mock logging handler to check for expected logs.

    Messages are available from an instance's ``messages`` dict,
    in order, indexed by a lowercase log level string (e.g.,
    'debug', 'info', etc.).

    Adapted from: http://stackoverflow.com/questions/899067/
    """

    def __init__(self, *args, **kwargs):
        self.messages = {'debug': [], 'info': [], 'warning': [], 'error': [],
                         'critical': []}
        super(MockLoggingHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        "Store a message from ``record`` in the instance's ``messages`` dict."
        self.acquire()
        try:
            self.messages[record.levelname.lower()].append(
                (record.getMessage(), record.exc_info))
        finally:
            self.release()

    def reset(self):
        self.acquire()
        try:
            for message_list in self.messages.values():
                del message_list[:]
        finally:
            self.release()
