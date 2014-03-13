import os
from testtools import TestCase
from mock import Mock, patch
from hashlib import md5


class ChunkedFileTest(TestCase):
    def setUp(self):
        super(ChunkedFileTest, self).setUp()
        self.home = os.path.join('t', 'data', 'home')
        self.testfile = os.path.join('t', 'data', 'longaccess-74-5N93.html')

    def tearDown(self):
        super(ChunkedFileTest, self).tearDown()

    def _makeit(self, *args, **kw):
        from lacli.source.chunked import ChunkedFile
        return ChunkedFile(*args,  **kw)

    def test_constructor_nopath(self):
        f = self._makeit('')
        self.assertFalse(f.isfile)

    def test_constructor_devnull(self):
        f = self._makeit(os.devnull)
        self.assertFalse(f.isfile)

    def test_constructor_file(self):
        f = self._makeit(self.testfile)
        self.assertTrue(f.isfile)

    def test_constructor_file_too_big_skip(self):
        self.assertRaises(AssertionError, self._makeit, self.testfile,
                          skip=50000000)

    def test_constructor_file_one_chunk(self):
        f = self._makeit(self.testfile, chunk=50000000000)
        self.assertEqual(1, f.chunks)

    def test_constructor_file_one_chunk2(self):
        f = self._makeit(os.path.join('t', 'data', 'empty.txt'))
        self.assertEqual(1, f.chunks)

    def test_chunkstart(self):
        fsz = os.path.getsize(self.testfile)
        for sz in [10, 15]:
            f = self._makeit(self.testfile, chunk=sz)
            last = int(fsz/sz)
            for chunk in range(last):
                if chunk > last:
                    self.assertRaises(ValueError, f.chunkstart, chunk)
                else:
                    self.assertEqual(chunk * sz, f.chunkstart(chunk))

    def test_chunksize(self):
        fsz = os.path.getsize(self.testfile)
        for sz in [10, 15]:
            f = self._makeit(self.testfile, chunk=sz)
            last = int(fsz/sz)
            lastsz = fsz % sz
            if lastsz > 0:
                last += 1
            else:
                lastsz = sz
            for chunk in range(last):
                if chunk == last - 1:
                    self.assertEqual(lastsz, f.chunksize(chunk))
                else:
                    self.assertEqual(sz, f.chunksize(chunk))
            self.assertRaises(ValueError, f.chunksize, last + 1)

    @patch('lacli.source.chunked.compute_md5')
    def test_filehash(self, compute_md5):
        from lacli.source.chunked import SavedPart

        compute_md5.return_value = ('MD5', 'B64MD5', 123)
        src = Mock()
        src.chunksize.return_value = 123
        f = SavedPart(src, 1, self.testfile)
        self.assertEqual(2, len(f.hash))
        self.assertEqual('MD5', f.hash[0])
        self.assertEqual('B64MD5', f.hash[1])
        self.assertEqual(123, f.bytes)
        src.chunksize.assert_called_with(1)

    def test_filepart(self):
        src = Mock()
        src.path = self.testfile
        src.chunkstart.return_value = 2
        src.chunksize.return_value = 7
        from lacli.source.chunked import FilePart
        f = FilePart(src, 1)
        src.chunksize.assert_called_with(1)
        src.chunkstart.assert_called_with(1)
        self.assertEqual('DOCTYPE', f.read())
        m = md5()
        m.update('DOCTYPE')
        self.assertEqual(m.hexdigest(), f.hash[0])
