# -*- coding: utf-8 -*-
import os

from datetime import datetime
from testtools import TestCase
from . import makeprefs, dummykey, _temp_home
from shutil import copy
from mock import patch, Mock, MagicMock
from contextlib import nested


class CacheTest(TestCase):
    def setUp(self):
        super(CacheTest, self).setUp()
        self.prefs = makeprefs()
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(CacheTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.cache import Cache
        return Cache(*args, **kwargs)

    def test_cache(self):
        assert self._makeit("")

    def test_prepare(self):
        with _temp_home() as home:
            cache = self._makeit(home)
            cache.prepare('foo', os.path.join('t', 'data', 'arc1'))
            archives = cache._for_adf('archives')
            self.assertEqual(len(archives), 1)
            self.assertEqual('foo',
                             next(archives.itervalues())['archive'].title)

    def test_cache_dir(self):
        d = 'archives'
        self.assertTrue(
            os.path.isdir(self._makeit(self.home)._cache_dir(d)))
        with _temp_home() as home:
            cache = self._makeit(home)
            self.assertFalse(os.path.exists(cache._cache_dir(d)))
            self.assertTrue(os.path.isdir(cache._cache_dir(d, write=True)))

    def test_archive_open(self):
        open_mock = Mock(return_value=None)
        import lacli.cache as cache
        with patch.object(cache, 'open', open_mock, create=True):
            with _temp_home() as home:
                cache = self._makeit(home)
                dname = os.path.join(home, 'archives')
                fname = os.path.join(dname, 'foo')
                cache._archive_open('foo', 'w')
                open_mock.assert_called_with(fname, 'w')
                self.assertTrue(os.path.isdir(dname))
                cache._cert_open('foo', 'w')
                dname = os.path.join(home, 'certs')
                fname = os.path.join(dname, 'foo')
                open_mock.assert_called_with(fname, 'w')
                self.assertTrue(os.path.isdir(dname))

    def test_certs(self):
        with _temp_home() as home:
            cache = self._makeit(home)
            self.assertEqual({}, cache.certs())
            cdir = os.path.join(home, 'certs')
            os.makedirs(cdir)
            certs = cache.certs()
            self.assertEqual(0, len(certs))
            copy(os.path.join(self.home, 'archives', 'sample.adf'), cdir)
            certs = cache.certs()
            self.assertEqual(1, len(certs))
            self.assertIn('12-345', certs)
            self.assertIn('archive', certs['12-345'])
            self.assertEqual('My 2013 vacation',
                             certs['12-345']['archive'].title)
            c = certs['12-345']['cert'].keys[1]
            self.assertTrue(hasattr(c, 'key'))
            self.assertTrue(hasattr(c, 'method'))
            self.assertTrue(hasattr(c, 'input'))
            self.assertEqual(dummykey, c.input)
            self.assertEqual(1, c.key)
            self.assertEqual('pbkdf2', c.method)

    def test_save_cert(self):
        import lacli.cache
        from lacore.adf.elements import Archive, Meta, Signature
        from StringIO import StringIO
        with nested(
                patch.object(lacli.cache, 'NamedTemporaryFile', create=True),
                patch.object(lacli.cache, 'archive_slug', create=True),
                ) as (mock_open, slug):
            out = StringIO()
            mock_open.return_value.__enter__.return_value = MagicMock()
            mock_open.return_value.__enter__.return_value.write = out.write
            now = datetime.utcfromtimestamp(0)
            meta = Meta('zip', 'xor', created=now)
            archive = Archive('foo', meta)
            slug.return_value = 'foo'
            cache = self._makeit(self.home)
            cache.save_cert({'archive': archive,
                             'signature': Signature(aid="foo",
                                                    uri="http://baz.com",
                                                    created=now)})
            args, kwargs = mock_open.call_args
            self.assertIn('prefix', kwargs)
            self.assertEqual(ADF_EXAMPLE_1, out.getvalue())

    def test_save_upload(self):
        import lacli.cache
        from lacore.adf.elements import Archive, Meta, Signature, Links
        from StringIO import StringIO
        with patch.object(lacli.cache, 'archive_slug', create=True) as slug:
            now = datetime.utcfromtimestamp(0)
            meta = Meta('zip', 'xor', created=now)
            archive = Archive('foo', meta)
            slug.return_value = 'foo'
            cache = self._makeit(self.home)
            out = StringIO()
            aopen = MagicMock()
            aopen.return_value.__enter__.return_value = MagicMock()
            aopen.return_value.__enter__.return_value.write = out.write
            cache._archive_open = aopen
            r = cache.save_upload('lalafname',
                                  {'archive': archive,
                                   'signature': Signature(aid="foo",
                                                          uri="http://baz.com",
                                                          created=now),
                                   'links': Links()},
                                  uri='http://foo.bar',
                                  capsule='Photos')
            self.assertEqual(
                r, {'fname': 'lalafname', 'link': 'http://foo.bar#C:Photos:',
                    'archive': archive})
            args, kwargs = aopen.call_args
            self.assertEqual(('lalafname', 'w'), args)
            self.assertEqual(ADF_EXAMPLE_2, out.getvalue())

    def test_import_cert(self):
        import lacli.cache
        with nested(
                patch.object(lacli.cache, 'NamedTemporaryFile', create=True),
                patch.object(lacli.cache, 'archive_slug', create=True),
                _temp_home()
                ) as (mock_open, slug, home):
            mock_open.return_value.__enter__.return_value = MagicMock()
            mock_open.return_value.__enter__.return_value.name = "bar"
            slug.return_value = 'foo'
            cache = self._makeit(home)
            cert = os.path.join('t', 'data', 'longaccess-74-5N93.html')
            aid, fname = cache.import_cert(cert)
            args, kwargs = mock_open.call_args
            self.assertIn('prefix', kwargs)
            self.assertEqual('bar', fname)
            self.assertEqual('74-5N93', aid)

    def test_upload_complete(self):
        import lacli.cache
        cache = self._makeit(self.home)
        with nested(
                patch.object(lacli.cache, 'open', create=True),
                patch.object(lacli.cache, 'load_archive', create=True),
                patch.object(lacli.cache, 'make_adf', create=True)
                ) as (mock_open, mock_load, mock_adf):
            from lacore.adf.elements import Archive, Meta
            now = datetime.utcfromtimestamp(0)
            meta = Meta('zip', 'xor', created=now)
            archive = Archive('foo', meta)
            mock_load.return_value = {'archive': archive}
            uri = 'http://longaccess.com/a'
            ds = cache.upload_complete("foo", {'archive_key': 'bar',
                                               'archive': uri})
            self.assertIn('signature', ds)
            self.assertEqual('bar', ds['signature'].aid)
            self.assertEqual(uri, ds['signature'].uri)


ADF_EXAMPLE_1 = """---
!archive {
  ? !!str "meta"
  : !meta {
    ? !!str "cipher"
    : !!str "xor",
    ? !!str "created"
    : !!timestamp "1970-01-01 00:00:00",
    ? !!str "format"
    : !!str "zip",
  },
  ? !!str "title"
  : !!str "foo",
}
---
!signature {
  ? !!str "aid"
  : !!str "foo",
  ? !!str "created"
  : !!timestamp "1970-01-01 00:00:00",
  ? !!str "expires"
  : !!timestamp "2000-01-01 00:00:00",
  ? !!str "uri"
  : !!str "http://baz.com",
}
"""


ADF_EXAMPLE_2 = """---
!archive {
  ? !!str "meta"
  : !meta {
    ? !!str "cipher"
    : !!str "xor",
    ? !!str "created"
    : !!timestamp "1970-01-01 00:00:00",
    ? !!str "format"
    : !!str "zip",
  },
  ? !!str "title"
  : !!str "foo",
}
---
!links {
  ? !!str "upload"
  : !!str "http://foo.bar#C:Photos:",
}
---
!signature {
  ? !!str "aid"
  : !!str "foo",
  ? !!str "created"
  : !!timestamp "1970-01-01 00:00:00",
  ? !!str "expires"
  : !!timestamp "2000-01-01 00:00:00",
  ? !!str "uri"
  : !!str "http://baz.com",
}
"""
