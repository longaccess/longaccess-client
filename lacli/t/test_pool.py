
from testtools import TestCase
from moto import mock_s3
from mock import Mock


class MPUploadTest(TestCase):

    def setUp(self):
        self.s3 = mock_s3()
        self.s3.start()

        super(MPUploadTest, self).setUp()

    def tearDown(self):
        self.s3.stop()
        super(MPUploadTest, self).tearDown()

    def _makeit(self, *args, **kw):
        from lacli.pool import MPUpload
        return MPUpload(*args,  **kw)

    def test_getupload_1(self):
        mp = self._makeit(Mock(newkey=Mock(return_value='baz')),
                          Mock(chunks=1), 'foo')
        self.assertEqual('baz', mp._getupload())
        mp.conn.newkey.assert_called_with('foo')

    def test_getupload_2(self):
        c = Mock()
        c.newupload.return_value = 'yo'
        mp = self._makeit(c, Mock(chunks=2), 'foo')
        self.assertEqual('yo', mp._getupload())
        c.newupload.assert_called_with('foo')
        c.getupload.return_value = Mock(id='bar')
        mp.upload_id = 'bar'
        self.assertEqual('bar', mp._getupload().id)
        c.getupload.assert_called()
