import os

from . import makeprefs
from testtools import TestCase
from mock import Mock, patch
from boto import connect_s3


class S3DumperTest(TestCase):
    @classmethod
    def setup_class(cls):
        cls._bucket = 'lastage2'

    def setUp(self):
        super(S3DumperTest, self).setUp()
        self.prefs = makeprefs()
        self.home = os.path.join('t', 'data', 'home')
        boto = connect_s3()
        boto.create_bucket(self._bucket)

    def tearDown(self):
        super(S3DumperTest, self).tearDown()

    def test_s3_constructor(self):
        from lacli.dumper.s3 import S3Dumper
        from lacli.storage.s3 import S3Connection
        dest = S3Dumper()
        self.assertTrue(isinstance(dest.connection, S3Connection))

    def test_s3_constructor_with_connection(self):
        from lacli.dumper.s3 import S3Dumper
        mockc = Mock()
        dest = S3Dumper(connection=mockc)
        self.assertEqual(dest.connection, mockc)

    def test_s3_dumper(self):
        fno = {'fileno.return_value': 0,
               'read.side_effect': ["file contents man", None]}
        mrsp = Mock(**fno)
        from lacli.dumper.s3 import S3Dumper
        from lacli.storage.s3 import S3Connection
        with patch('lacli.archive.urls.urlopen', Mock(return_value=mrsp)):
            c = S3Connection(bucket=self._bucket)
            dest = S3Dumper(key='baz', connection=c, title='foo')
            cb = Mock()
            list(dest.dump(['http://foobar'], cb))
            self.assertEqual(160, dest.docs['archive'].meta.size)
            from hashlib import md5
            m = md5()
            m.update(c.bucket.lookup('baz').get_contents_as_string())
            self.assertEqual(m.digest().encode('hex'),
                             dest.docs['auth'].md5.encode('hex'))
