# -*- coding: utf-8 -*-
from testtools import TestCase
from mock import Mock
from binascii import a2b_hex, b2a_hex

#  NIST test vectors (last one is ours, uses padding)
KEY = '603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4'
IV = 'f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff'
VECTORS = (
    ('6bc1bee22e409f96e93d7e117393172a', '601ec313775789a5b7a7f504bbf3d228'),
    ('ae2d8a571e03ac9c9eb76fac45af8e51', 'f443e3ca4d62b59aca84e990cacaf5c5'),
    ('30c81c46a35ce411e5fbc1191a0a52ef', '2b0930daa23de94ce87017ba2d84988d'),
    ('f69f2445df4f9b17ad2b417be66c3710', 'dfc9c58db67aada613c2dd08457941a6'),
    ('2ab7a7bc7f73420932',               'a1c0585ca60f4b9be5f0091beec8c4b0'))


class CipherAESTest(TestCase):

    def setUp(self):
        super(CipherAESTest, self).setUp()

    def tearDown(self):
        super(CipherAESTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.cipher.aes import CipherAES
        return CipherAES(*args, **kwargs)

    def test_encipher_invalid(self):
        self.assertRaises(ValueError, self._makeit, None, None)

    def test_encipher(self):
        cipher = self._makeit(Mock(key=a2b_hex(KEY)),
                              Mock(input=a2b_hex(IV)))
        for p, c in VECTORS:
            if len(a2b_hex(p)) < cipher.BLOCKSIZE:
                self.assertEqual(c, b2a_hex(cipher.encipher(a2b_hex(p))) +
                                 b2a_hex(cipher.flush()))
            else:
                self.assertEqual(c, b2a_hex(cipher.encipher(a2b_hex(p))))

    def test_encipher_all(self):
        cipher = self._makeit(Mock(key=a2b_hex(KEY)),
                              Mock(input=a2b_hex(IV)))
        pt = "".join([v[0] for v in VECTORS])
        ct = "".join([v[1] for v in VECTORS])
        self.assertEqual(ct, b2a_hex(cipher.encipher(a2b_hex(pt))) +
                         b2a_hex(cipher.flush()))

    def test_encipher_flush(self):
        cipher = self._makeit(Mock(key=a2b_hex(KEY)),
                              Mock(input=a2b_hex(IV)))
        pt = VECTORS[0][0]
        ct = VECTORS[0][1]
        self.assertEqual(ct, b2a_hex(cipher.encipher(a2b_hex(pt))))

    def test_flush(self):
        cipher = self._makeit(Mock(key="0"*32))
        # padding = a2b_hex("10"*16)
        # ct = b2a_hex(self._makeit(Mock(key="0"*32)).encipher_block(padding))
        ct = '2b9cf21e2f5611a68ab213aa44972cf0'
        self.assertEqual(ct, b2a_hex(cipher.flush()))

    def test_decipher(self):
        cipher = self._makeit(Mock(key=a2b_hex(KEY)),
                              Mock(input=a2b_hex(IV)))
        for i in range(len(VECTORS)+1):
            p = c = ''
            last = i == len(VECTORS)
            if i:
                p = VECTORS[i-1][0]
            if not last:
                c = VECTORS[i][1]
            self.assertEqual(p, b2a_hex(cipher.decipher(a2b_hex(c), last)))

    def test_decipher_all(self):
        cipher = self._makeit(Mock(key=a2b_hex(KEY)),
                              Mock(input=a2b_hex(IV)))
        pt = "".join([v[0] for v in VECTORS])
        ct = "".join([v[1] for v in VECTORS])
        self.assertEqual(pt, b2a_hex(cipher.decipher(a2b_hex(ct), True)))
