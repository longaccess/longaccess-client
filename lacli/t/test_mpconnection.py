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
            'token_uid': '',
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
        from lacli.pool import MPConnection
        return MPConnection(*args,  **kw)

    def test_mpconnection(self):
        assert self._makeit(self._token)

    def test_mpconnection_nouid(self):
        token = self._token
        token['token_uid'] = None
        assert self._makeit(token)

    def test_getconnection(self):
        conn = self._makeit(self._token)
        assert conn.getconnection()

    def test_getbucket(self):
        conn = self._makeit(self._token)
        bucket = conn.getbucket()
        self.assertEqual(bucket.name, self._bucket)

    @patch('lacli.pool.getLogger', create=True)
    def test_timeout(self, log):
        tok = self._token
        tok['token_expiration'] = "this is not a timestamp"
        conn = self._makeit(tok, grace=0)
        self.assertEqual(None, conn.timeout())
        log.assert_called_with()
        log.return_value.debug.assert_called_with(
            'invalid token expiration: %s', 'this is not a timestamp')
        tok['token_expiration'] = datetime.utcnow().isoformat()
        conn = self._makeit(tok, grace=0)
        self.assertEqual(0, int(conn.timeout()))
        tok['token_expiration'] = datetime.utcnow()
        conn = self._makeit(tok, grace=0)
        self.assertEqual(0, int(conn.timeout()))
        tok['token_expiration'] = datetime.utcnow()+relativedelta(seconds=100)
        conn = self._makeit(tok, grace=100)
        self.assertEqual(0, int(conn.timeout()))
        tok['token_expiration'] = datetime.utcnow()+relativedelta(seconds=101)
        conn = self._makeit(tok, grace=0)
        self.assertEqual(100, int(conn.timeout()))
