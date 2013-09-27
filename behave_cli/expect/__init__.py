from pexpect import EOF, TIMEOUT

import os


def expected_text(child, text):
    index = child.expect_exact([text, TIMEOUT, EOF], timeout=10)

    return index == 0


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


def python_cmd(module, func, args):
    call_stmt = "from {m} import {f}; {f}();".format(m=module, f=func)
    return "python -c '{c}' {a}".format(c=call_stmt, a=args)
