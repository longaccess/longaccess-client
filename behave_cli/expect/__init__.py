from pexpect import EOF, TIMEOUT

import os


def expected_text(child, text):
    index = child.expect_exact([text, TIMEOUT, EOF], timeout=10)

    return index == 0


def setup(context):
    context.environ = {}
    context.child = None
    context.children = {}
    context.cwd = os.getcwd()
    context.args = None


def teardown(context):
    for child in context.children.values():
        child.__proc.join()
        child.close()
    context.child = None
    context.children = {}
    context.args = None
