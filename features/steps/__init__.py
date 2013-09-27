from behave_cli.expect.steps import *
from behave_cli.files.steps import *
from behave_cli.api.steps import *
from behave_cli.s3mock.steps import *
from behave_cli.s3mock import setup as s3setup
from behave_cli.s3mock import teardown as s3teardown
from mock import patch
import requests


class PatchedSession(requests.Session):
    def __init__(self, *args, **kwargs):
        super(PatchedSession, self).__init__(*args, **kwargs)
        self.headers['connection'] = 'Close'


def mp_setup(ctx):
    s3setup(ctx)
    ctx.patcher = patch('requests.Session', PatchedSession)
    ctx.patcher.start()


def mp_teardown(ctx):
    ctx.patcher.stop()
    s3teardown(ctx)
