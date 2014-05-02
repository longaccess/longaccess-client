from behave_cli.expect.steps import *  # noqa
from behave_cli.files.steps import *  # noqa
from behave_cli.api.steps import *  # noqa
from behave_cli.s3mock.steps import *  # noqa
from behave_cli.netrc.steps import *  # noqa
from behave_cli.s3mock import setup as s3setup
from behave_cli.s3mock import teardown as s3teardown
from behave_cli.s3mock.steps import s3bucket_named
from Crypto import Random


def mp_setup(ctx):
    buckets = ctx.buckets  # save buckets before setup resets them
    s3setup(ctx)
    if len(buckets):
        for bucket in buckets:
            s3bucket_named(ctx, bucket)
    Random.atfork()


def mp_teardown(ctx):
    s3teardown(ctx)


def cert_vars(ctx):
    return {'certid': ctx.certid}
