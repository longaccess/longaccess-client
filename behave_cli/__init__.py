import os


def setup(context):
    context.environ = os.environ.copy()
    context.child = None
    context.children = {}
    context.cwd = os.getcwd()
    context.args = None


def teardown(context):
    for child in context.children.values():
        child.close()
    context.child = None
    context.children = {}
    context.args = None
