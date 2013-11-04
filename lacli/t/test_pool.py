from testtools import TestCase
from mock import Mock, MagicMock


class MPConnectionTest(TestCase):
    def setUp(self):
        super(MPConnectionTest, self).setUp()

    def tearDown(self):
        super(MPConnectionTest, self).tearDown()

    def _makeit(self, *args, **kw):
        from lacli.pool import MPConnection
        return MPConnection(*args,  **kw)

    def _token(self, uid=None):
        return { 
            'token_access_key': None,
            'token_secret_key': None,
            'token_session': None,
            'token_expiration': None,
            'token_uid': uid,
            'bucket': None
            }

    def test_makeit(self):
        assert self._makeit(MagicMock(), 4)

    def test_no_expiration(self):
        conn = self._makeit(self._token("lala"), 4)
        self.assertEqual(None, conn.timeout())

    def test_timeout_parse_error(self):
        token = self._token("lala")
        token['token_expiration'] = "foobar"
        conn = self._makeit(token, 4)
        self.assertEqual(None, conn.timeout())
