def setup(context):
    context.file = None
    context.files = {}


def teardown(context):
    for file in context.files.values():
        file.close()
    context.file = None
    context.files = {}
