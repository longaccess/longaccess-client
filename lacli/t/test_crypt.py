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

    def _mockfile(self):
        return Mock(mode='wb', write=Mock())

    def test_cryptio(self):
        self.assertRaises(ValueError, self._makeit, None, None)
        self.assertRaises(ValueError, self._makeit, None, Mock())
        self.assertRaises(ValueError, self._makeit, self._mockfile(), None)
        obj = self._makeit(self._mockfile(), Mock())
        self.assertTrue(obj.writable())

    def test_cryptio_nomode(self):
        f = self._mockfile()
        del f.mode
        self._makeit(f, Mock())

    def test_cryptio_badmode(self):
        self.assertRaises(IOError, self._makeit, Mock(mode='r'), Mock())

    @raises(ValueError)
    def test_cryptio_write_closed(self):
        f = self._mockfile()
        c = self._makeit(f, Mock())
        c.close()
        c.close()
        c.write("FOO")

    def test_cryptio_memoryview(self):
        f = self._mockfile()
        c = self._makeit(f, Mock())
        c.write(memoryview("FOO"))
