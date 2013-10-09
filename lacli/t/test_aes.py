# -*- coding: utf-8 -*-
from testtools import TestCase


class CipherAESTest(TestCase):
    def setUp(self):
        super(CipherAESTest, self).setUp()

    def tearDown(self):
        super(CipherAESTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.cipher.aes import CipherAES
        return CipherAES(*args, **kwargs)

    def test_encipher(self):
        cipher = self._makeit(None)
        self.assertEquals("foo", cipher.encipher("foo"))

    def test_flush(self):
        cipher = self._makeit(None)
        self.assertFalse(cipher.flush())
