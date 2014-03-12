from testtools import TestCase
from moto import mock_s3
from boto import connect_s3
from datetime import datetime
from dateutil.relativedelta import relativedelta
from mock import patch


class MPConnectionTest(TestCase):
    @classmethod
    def setup_class(cls):
        cls._token = {
            'token_access_key': '',
            'token_secret_key': '',
            'token_session': '',
            'token_expiration': '',
            'bucket': 'lastage',
            'prefix': 'upload/14/',
        }
        cls._bucket = 'lastage'

    def setUp(self):
        self.s3 = mock_s3()
        self.s3.start()
        boto = connect_s3()
        boto.create_bucket(self._bucket)

        super(MPConnectionTest, self).setUp()

    def tearDown(self):
        self.s3.stop()
        super(MPConnectionTest, self).tearDown()

    def _makeit(self, *args, **kw):
        from lacli.storage.s3 import MPConnection
        return MPConnection(*args,  **kw)

    def test_mpconnection(self):
        assert self._makeit(**self._token)

    @patch('lacli.storage.s3.getLogger', create=True)
    def test_timeout(self, log):
        tok = self._token
        tok['token_expiration'] = "this is not a timestamp"
        conn = self._makeit(grace=0, **tok)
        self.assertEqual(None, conn.timeout())
        log.assert_called_with()
        log.return_value.debug.assert_called_with(
            'invalid token expiration: %s', 'this is not a timestamp')
        tok['token_expiration'] = datetime.utcnow().isoformat()
        conn = self._makeit(grace=0, **tok)
        self.assertEqual(0, int(conn.timeout()))
        tok['token_expiration'] = datetime.utcnow()
        conn = self._makeit(grace=0, **tok)
        self.assertEqual(0, int(conn.timeout()))
        tok['token_expiration'] = datetime.utcnow()+relativedelta(seconds=100)
        conn = self._makeit(grace=100, **tok)
        self.assertEqual(0, int(conn.timeout()))
        tok['token_expiration'] = datetime.utcnow()+relativedelta(seconds=101)
        conn = self._makeit(grace=0, **tok)
        self.assertEqual(100, int(conn.timeout()))
