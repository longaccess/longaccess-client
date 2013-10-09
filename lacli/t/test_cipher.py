# -*- coding: utf-8 -*-
from nose.tools import raises
from testtools import TestCase


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
                super(Foo, self).flush()
        return Foo(*args, **kwargs)

    def test_cipher(self):
        from lacli.cipher import UnsupportedOperation
        foo = self._makeit()
        self.assertRaises(UnsupportedOperation, foo.encipher, "")

    def test_flush(self):
        self._makeit().flush()
