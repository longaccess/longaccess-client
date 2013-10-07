import os
from shutil import rmtree

try:
    from behave_cli import logger as logging
except ImportError:
    import logging


def ferror(f, p, x):
    logging.error("{}: {}".format(p, x[1].strerror))


def setup(context):
    context.files = {}
    context.dirs = {}
    context.fifo = {}


def teardown(context):
    for f in context.files.values():
        f.close()
    for d in context.dirs.values():
        f = os.path.join(d, 'fifo')
        if os.path.exists(f):
            os.remove(f)
            context.fifo[f].join()
        rmtree(d, onerror=ferror)
    context.files = {}
