from behave_cli.expect.steps import *
from behave_cli.files.steps import *
from behave_cli.api.steps import *
from behave_cli.s3mock.steps import *
from behave_cli.netrc.steps import *
from behave_cli.s3mock import setup as s3setup
from behave_cli.s3mock import teardown as s3teardown
from behave_cli.s3mock.steps import s3bucket_named


def mp_setup(ctx):
    buckets = ctx.buckets  # save buckets before setup resets them
    s3setup(ctx)
    if len(buckets):
        for bucket in buckets:
            s3bucket_named(ctx, bucket)


def mp_teardown(ctx):
    s3teardown(ctx)
