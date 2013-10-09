# -*- coding: utf-8 -*-
from testtools import TestCase
from nose.tools import raises
from mock import Mock


class CryptIOTest(TestCase):
    def setUp(self):
        super(CryptIOTest, self).setUp()

    def tearDown(self):
        super(CryptIOTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.crypt import CryptIO
        return CryptIO(*args, **kwargs)

    def _mockfile(self, mode='rb', read=None):
        return Mock(mode=mode, write=Mock(), read=(read or Mock()))

    def _makecipher(self):
        return Mock(encipher=lambda x: x,
                    decipher=lambda x: x,
                    BLOCKSIZE=32,
                    flush=lambda: '')

    def test_cryptio(self):
        self.assertRaises(ValueError, self._makeit, None, None)
        self.assertRaises(ValueError, self._makeit, None, None, mode='w')
        self.assertRaises(ValueError, self._makeit, None, Mock())
        mockf = self._mockfile(mode='wb')
        self.assertRaises(ValueError, self._makeit, mockf, None)
        obj = self._makeit(mockf, Mock())
        self.assertTrue(obj.writable())
        obj = self._makeit(self._mockfile(), Mock(), mode='rU')
        self.assertTrue(obj.readable())
        dec = Mock()
        del dec.decipher
        mockf = self._mockfile()
        self.assertRaises(ValueError, self._makeit, mockf, dec)

    def test_cryptio_nomode(self):
        f = self._mockfile()
        del f.mode
        self._makeit(f, Mock())

    def test_cryptio_badmode(self):
        self.assertRaises(IOError, self._makeit, Mock(mode='foo'), Mock())

    def test_write_to_read(self):
        f = self._makeit(self._mockfile(), Mock())
        self.assertRaises(IOError, f.write, "")

    def test_read_from_write(self):
        f = self._makeit(self._mockfile('wb'), Mock())
        self.assertRaises(IOError, f.read)

    @raises(ValueError)
    def test_cryptio_write_closed(self):
        f = self._mockfile(mode='wb')
        c = self._makeit(f, Mock())
        c.close()
        c.close()
        c.write("FOO")

    @raises(ValueError)
    def test_cryptio_read_closed(self):
        f = self._mockfile()
        c = self._makeit(f, Mock())
        c.close()
        c.read()

    def test_cryptio_memoryview(self):
        f = self._mockfile(mode='wb')
        c = self._makeit(f, Mock())
        c.write(memoryview("FOO"))

    def test_read(self):
        fdata = ['0'*1024 for _ in range(5)]
        fdata.append('')
        fdata.append(EOFError)
        f = self._mockfile(read=Mock(side_effect=fdata))
        c = self._makeit(f, self._makecipher())
        out = c.read(500)
        self.assertEqual(500, len(out))
        out += c.read(524)
        self.assertEqual(1024, len(out))
        out += c.read()
        self.assertEqual(5*1024, len(out))
        out += c.read()
        self.assertEqual(5*1024, len(out))

    def test_write(self):
        import StringIO
        f = StringIO.StringIO()
        c = self._makeit(f, self._makecipher(), mode='wb')
        d = '0' * 100
        for _ in range(5):
            c.write(d)
        c.flush()
        self.assertEqual(500, len(f.getvalue()))
