import pickle

from testtools import TestCase
from moto import mock_s3
from boto import connect_s3


class S3ConnectionTest(TestCase):
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

        super(S3ConnectionTest, self).setUp()

    def tearDown(self):
        self.s3.stop()
        super(S3ConnectionTest, self).tearDown()

    def _makeit(self, *args, **kw):
        from lacli.storage.s3 import S3Connection
        return S3Connection(*args,  **kw)

    def test_s3connection(self):
        assert self._makeit(**self._token)

    def test_getconnection(self):
        conn = self._makeit(**self._token)
        assert conn.getconnection()

    def test_getbucket(self):
        conn = self._makeit(**self._token)
        self.assertEqual(conn.bucket.name, self._bucket)

    def test_newkey(self):
        conn = self._makeit(**self._token)
        key = conn.newkey('foobar')
        self.assertEqual(conn.bucket.name, key.bucket.name)
        self.assertEqual('upload/14/foobar', key.name)

    def test_pickle(self):
        conn = self._makeit(**self._token)
        conn.getconnection()
        self.assertTrue(conn.conn is not None)
        conn = pickle.loads(pickle.dumps(conn))
        self.assertTrue(conn.conn is None)
