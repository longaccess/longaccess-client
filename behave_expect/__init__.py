import os


def setup(context):
    context.environ = os.environ.copy()
    context.child = None
    context.children = {}
    context.cwd = os.getcwd()


def teardown(context):
    for child in context.children.values():
        child.close()
    context.child = None
    context.children = {}
