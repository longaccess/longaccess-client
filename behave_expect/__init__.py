import os


def setup(context):
    context.environ = os.environ.copy()
