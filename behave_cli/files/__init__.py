def setup(context):
    context.files = {}
    context.dirs = {}


def teardown(context):
    for f in context.files.values():
        f.close()
    context.files = {}
