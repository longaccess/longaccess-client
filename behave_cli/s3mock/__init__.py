from moto import mock_s3
import requests
from mock import patch


class PatchedSession(requests.Session):
    def __init__(self, *args, **kwargs):
        super(PatchedSession, self).__init__(*args, **kwargs)
        self.headers['connection'] = 'Close'


def setup(context):
    context.moto = mock_s3()
    context.moto.start()
    context.patcher = patch('requests.Session', PatchedSession)
    context.patcher.start()
    context.buckets = []


def teardown(context):
    context.patcher.stop()
    context.moto.stop()
