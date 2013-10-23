from testtools import TestCase
from struct import unpack
from nose.tools import raises
from mock import Mock


class AdfTest(TestCase):
    def setUp(self):
        super(AdfTest, self).setUp()

    def tearDown(self):
        super(AdfTest, self).tearDown()

    def _archive(self, title='', format='', cipher=''):
        from lacli.adf import Archive, Meta
        return Archive(title, Meta(format, cipher, created='now'))

    def test_archive(self):
        from lacli.adf import make_adf
        self.assertEqual(ADF_TEST_DATA_1,
                         make_adf(self._archive('foo'), True))

    @raises(ValueError)
    def test_archive_invalid(self):
        from lacli.adf import Archive
        Archive('foo', {})

    def test_unicode(self):
        from lacli.adf import make_adf
        self.assertEqual(ADF_TEST_DATA_1,
                         make_adf(self._archive('foo'), True))

    def test_meta(self):
        from lacli.adf import Meta, make_adf
        meta = make_adf(Meta(
            format='zip', cipher='aes-256-ctr', created='now'), True)
        self.assertEqual(meta, ADF_TEST_DATA_2)

    def test_links(self):
        from lacli.adf import Links, make_adf
        links = make_adf(Links(upload='foo', local='bar'), True)
        self.assertEqual(ADF_TEST_DATA_3, links)

    def test_signature(self):
        from lacli.adf import Signature, make_adf
        sig = make_adf(Signature(aid='bar', uri='foo', created='1'), True)
        self.assertEqual(ADF_TEST_DATA_4, sig)

    def test_minimal(self):
        from lacli.adf import load_archive

        with open('t/data/home/archives/minimal.adf') as f:
            docs = load_archive(f)
            self.assertEqual(docs['archive'].meta.cipher, 'aes-256-ctr')
            b = unpack("<LLLLLLLL", docs['cert'].key)
            self.assertEqual(b[0], 1911376514)

    def test_sample(self):
        from lacli.adf import load_archive

        with open('t/data/home/archives/sample.adf') as f:
            docs = load_archive(f)
            self.assertEqual(docs['archive'].meta.cipher.mode, 'aes-256-ctr')
            b = unpack("<LLLLLLLL", docs['archive'].meta.cipher.input)
            self.assertEqual(b[0], 1911376514)
            b = unpack("<LLLLLLLL", docs['cert'].keys[1].input)
            self.assertEqual(b[0], 1911376514)

    def test_cipher(self):
        from lacli.adf import Cipher
        self.assertRaises(ValueError, Cipher, 'foo', 1)
        self.assertRaises(ValueError, Cipher, 'aes-256-ctr', 'f')
        Cipher('xor', key=1)
        Cipher('xor', key=2, input=Mock())

ADF_TEST_DATA_1 = """---
!archive {
  ? !!str "meta"
  : !meta {
    ? !!str "cipher"
    : !!str "",
    ? !!str "created"
    : !!str "now",
    ? !!str "format"
    : !!str "",
  },
  ? !!str "title"
  : !!str "foo",
}
"""

ADF_TEST_DATA_2 = """---
!meta {
  ? !!str "cipher"
  : !!str "aes-256-ctr",
  ? !!str "created"
  : !!str "now",
  ? !!str "format"
  : !!str "zip",
}
"""

ADF_TEST_DATA_3 = """---
!links {
  ? !!str "local"
  : !!str "bar",
  ? !!str "upload"
  : !!str "foo",
}
"""

ADF_TEST_DATA_4 = """---
!signature {
  ? !!str "aid"
  : !!str "bar",
  ? !!str "created"
  : !!str "1",
  ? !!str "uri"
  : !!str "foo",
}
"""
