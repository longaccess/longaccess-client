
from testtools import TestCase, ExpectedException
from moto import mock_s3
from mock import Mock, patch
import monoprocessing


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

    def test_submit_job(self):
        source = Mock(chunks=1, isfile=True)
        mp = self._makeit(Mock(), source, 'foo')
        with patch.object(mp, 'do_part') as do_part:
            do_part.return_value = 'FooKey'
            rs = mp.submit_job(monoprocessing.Pool())
            self.assertEqual('FooKey', next(rs))
            with ExpectedException(StopIteration):
                next(rs)

    def test_get_result_empty(self):
        rs = Mock()
        rs.next.side_effect = StopIteration
        source = Mock(chunks=1, isfile=True)
        mp = self._makeit(Mock(), source, 'foo')
        from lacore.exceptions import UploadEmptyError
        self.assertRaises(UploadEmptyError, mp.get_result, rs)

    def test_get_result_exc_mp(self):
        rs = Mock()
        rs.next.side_effect = [Mock(etag='foo'), StopIteration]
        source = Mock(chunks=1, isfile=True)
        mp = self._makeit(Mock(), source, 'foo')
        from lacli.exceptions import CloudProviderUploadError
        mp.upload = Mock()
        mp.conn.complete_multipart.side_effect = Exception
        with ExpectedException(CloudProviderUploadError):
            mp.get_result(rs)
        mp.conn.complete_multipart.assert_called_with(mp.upload, ['foo'])

    @patch('lacli.pool.save_progress')
    def test_get_result(self, sp):
        rs = Mock()
        rs.next.side_effect = [Mock(etag='footag'), StopIteration]
        source = Mock(chunks=1, isfile=True, size=123)
        mp = self._makeit(Mock(), source, 'foo')
        mp.upload = Mock()
        mp.conn.complete_multipart.return_value = Mock(
            key_name='bar', etag='bartag')
        etag, source = mp.get_result(rs)
        sp.assert_called_with('bar', 123)
        mp.conn.complete_multipart.assert_called_with(mp.upload, ['footag'])
        self.assertTrue(source is None)

    @patch('lacli.pool.save_progress')
    @patch('lacli.pool.make_progress')
    @patch('lacli.pool.ChunkedFile')
    def test_get_result2(self, cf, mkp, svp):
        rs = Mock()
        rs.next.side_effect = [Mock(etag='footag'), StopIteration]
        source = Mock(chunks=2, isfile=True, size=123)
        source.chunkstart.return_value = 666
        cf.return_value = Mock(size=23)
        mp = self._makeit(Mock(), source, 'foo')
        mp.upload = Mock()
        mp.conn.complete_multipart.return_value = Mock(
            key_name='bar', etag='bartag')
        etag, newsource = mp.get_result(rs)
        svp.assert_called_with('bar', 100)
        mkp.assert_called_with({'part': 1, 'tx': 0})
        mp.conn.complete_multipart.assert_called_with(mp.upload, ['footag'])
        source.chunkstart.assert_called_with(1)
        cf.assert_called_with(source.path, skip=666, chunk=source.chunk)
        self.assertEqual(newsource.size, 23)
