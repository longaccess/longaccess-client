from behave_cli.expect.steps import *
from behave_cli.files.steps import *
from behave_cli.api.steps import *
from behave_cli.s3mock.steps import *
from behave_cli.s3mock import setup as s3setup
from behave_cli.s3mock import teardown as s3teardown


def mp_setup(ctx):
    s3setup(ctx)


def mp_teardown(ctx):
    s3teardown(ctx)
