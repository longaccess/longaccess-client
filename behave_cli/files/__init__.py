import os


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
        os.rmdir(d)
    context.files = {}
