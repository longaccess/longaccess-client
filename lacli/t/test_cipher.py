# -*- coding: utf-8 -*-
from nose.tools import raises
from testtools import TestCase
from mock import Mock
from binascii import a2b_hex, b2a_hex


class CipherTest(TestCase):
    def setUp(self):
        super(CipherTest, self).setUp()

    def tearDown(self):
        super(CipherTest, self).tearDown()

    @raises(TypeError)
    def test_cipher_base(self):
        from lacli.cipher import CipherBase
        CipherBase()

    @raises(TypeError)
    def test_cipher_base_inherit(self):
        from lacli.cipher import CipherBase

        class Foo(CipherBase):
            pass
        Foo()

    def _makeit(self, *args, **kwargs):
        from lacli.cipher import CipherBase

        class Foo(CipherBase):
            def flush(self):
                return super(Foo, self).flush()

            def encipher_block(self, block):
                return block
        return Foo(*args, **kwargs)

    def test_cipher(self):
        cipher = self._makeit()
        self.assertFalse(cipher.encipher("0"*8))
        self.assertEqual("0"*16, cipher.encipher("0"*20))
        self.assertEqual("0"*16, cipher.encipher("0000"))

    def test_xor(self):
        from lacli.cipher.xor import CipherXOR
        self.assertRaises(ValueError, CipherXOR, Mock(key='1'))
        cipher = CipherXOR(Mock(key=a2b_hex('ff00ff00ff00ff00')))
        self.assertEqual("5aa55aa55aa55aa5"*2+"f708f708f708f708", b2a_hex(
            cipher.encipher(a2b_hex('a5a5a5a5a5a5a5a5'*2))+cipher.flush()))
        self.assertEqual("fb04fb04fb04fb04", b2a_hex(cipher.encipher(
            a2b_hex('04040404'))+cipher.flush()))

    def test_pad(self):
        cipher = self._makeit()
        padded = cipher._pad(a2b_hex("00"*10))
        self.assertEqual("00"*10+"06"*6, b2a_hex(padded))
        self.assertEqual("00"*10, b2a_hex(cipher._unpad(padded)))
