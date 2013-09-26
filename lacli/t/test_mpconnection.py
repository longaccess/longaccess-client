from testtools import TestCase
from moto import mock_s3


class MPConnectionTest(TestCase):
    @classmethod
    def setup_class(cls):
        cls._token = {
            'token_access_key': '',
            'token_secret_key': '',
            'token_session': '',
            'token_expiration': '',
            'token_uid': '',
        }

    def _makeit(self, *args, **kw):
        from lacli.pool import MPConnection
        return MPConnection(*args,  **kw)

    def test_mpconnection(self):
        assert self._makeit(self._token)

    @mock_s3
    def test_mpconnection_nouid(self):
        token = self._token
        token['token_uid'] = None
        assert self._makeit(token)

    def test_getconnection(self):
        conn = self._makeit(self._token)
        assert conn.getconnection()

    def test_getbucket(self):
        assert self._makeit(self._token)
