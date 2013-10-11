# -*- coding: utf-8 -*-
from nose.tools import raises
from testtools import TestCase
from binascii import a2b_hex, b2a_hex
from mock import Mock, patch


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
            mode = 'foo'
        Foo()

    def _makeit(self, *args, **kwargs):
        from lacli.cipher import CipherBase

        class Foo(CipherBase):
            mode = 'foo'

            def flush(self):
                return super(Foo, self).flush()

            def encipher_block(self, block):
                return block

            def decipher_block(self, block):
                return block
        return Foo(*args, **kwargs)

    def test_cipher(self):
        cipher = self._makeit()
        self.assertFalse(cipher.encipher("0"*8))
        self.assertEqual("0"*16, cipher.encipher("0"*20))
        self.assertEqual("0"*16, cipher.encipher("0000"))

    def test_decipher(self):
        c1 = self._makeit()
        c2 = self._makeit()
        self.assertFalse(c2.decipher(c1.encipher("0"*8)))
        self.assertFalse(c2.decipher(c1.encipher("0"*20)))
        self.assertEqual("0"*32, c2.decipher(c1.encipher("0"*24)))
        self.assertEqual("0"*20, c2.decipher(c1.flush(), True))

    def test_decipher_remaining(self):
        cipher = self._makeit()
        self.assertFalse(cipher.decipher("0"*28))
        self.assertRaises(ValueError, cipher.decipher, "000000", True)

    def test_xor(self):
        from lacli.cipher.xor import CipherXOR
        self.assertRaises(ValueError, CipherXOR, '1')
        cipher = CipherXOR(a2b_hex('ff00ff00ff00ff00'))
        self.assertEqual("5aa55aa55aa55aa5"*2+"f708f708f708f708", b2a_hex(
            cipher.encipher(a2b_hex('a5a5a5a5a5a5a5a5'*2))+cipher.flush()))
        self.assertEqual("fb04fb04fb04fb04", b2a_hex(cipher.encipher(
            a2b_hex('04040404'))+cipher.flush()))

    def test_xor_dec(self):
        from lacli.cipher.xor import CipherXOR
        c1 = CipherXOR(a2b_hex('ff00ff00ff00ff00'))
        c2 = CipherXOR(a2b_hex('ff00ff00ff00ff00'))
        self.assertFalse(c2.decipher(c1.encipher("a5a5")))  # 4
        self.assertEqual("a5"*8, c2.decipher(c1.encipher("a5"*12)))  # 24
        self.assertEqual("a5"*6, c2.decipher(c1.flush(), True))

    def test_pad(self):
        cipher = self._makeit()
        padded = cipher._pad(a2b_hex("00"*10))
        self.assertEqual("00"*10+"06"*6, b2a_hex(padded))
        self.assertEqual("00"*10, b2a_hex(cipher._unpad(padded)))

    def test_get_cipher(self):
        from lacli.adf import Archive, Meta, Cipher
        from lacli.cipher import get_cipher
        with patch('lacli.cipher.xor.CipherXOR.__init__') as xorinit:
            xorinit.return_value = None
            archive = Archive('foo', Meta('zip', Cipher('xor', 1, 'bar')))
            get_cipher(archive, Mock(key='baz'))
            xorinit.assert_called_with('baz', 'bar')
            cert = Mock(keys=['baz'])
            del cert.key
            get_cipher(archive, cert)
            xorinit.assert_called_with('baz', 'bar')
            archive = Archive('foo', Meta('zip', Cipher('xor', 2, 'bar')))
            cert = Mock(keys=['baz', 'spam'])
            del cert.key
            get_cipher(archive, cert)
            archive = Archive('foo', Meta('zip', 'xor'))
            cert = Mock(keys=['baz', 'spam'])
            del cert.key
            get_cipher(archive, cert)
