# -*- coding: utf-8 -*-
import os

from testtools import TestCase
from . import makeprefs, dummykey, dummyurl, _temp_home
from shutil import copy
from mock import patch, Mock


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

    def test_archives_empty(self):
        self.assertEqual(self._makeit("doesnotexist").archives(), [])

    def test_archives(self):
        archives = self._makeit(self.home).archives()
        self.assertEqual(len(archives), 2)

    def test_prepare(self):
        with _temp_home() as home:
            cache = self._makeit(home)
            cache.prepare('foo', os.path.join('t', 'data', 'arc1'))
            archives = cache.archives()
            self.assertEqual(len(archives), 1)
            self.assertEqual(archives[0].title, 'foo')

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

#    def test_title_cert(self):
#        cache = self._makeit(self.home)
#        ds = Mock(keys=[], title='foo', key='bar')
#        self.assertEqual(('foo', ['bar']), cache._title_cert([ds]))
#        del ds.key
#        del ds.keys
#        self.assertEqual(('foo', []), cache._title_cert([ds]))
#        del ds.title
#        self.assertFalse(cache._title_cert([ds]))

    def test_certs(self):
        with _temp_home() as home:
            cache = self._makeit(home)
            self.assertEqual({}, cache.certs())
            cdir = os.path.join(home, 'certs')
            os.makedirs(cdir)
            copy(os.path.join(self.home, 'archives', 'minimal.adf'), cdir)
            certs = cache.certs()
            self.assertEqual(1, len(certs))
            self.assertTrue('milos 2013' in certs)
            self.assertEqual(dummykey, certs['milos 2013'].key)
            copy(os.path.join(self.home, 'archives', 'sample.adf'), cdir)
            certs = cache.certs()
            self.assertEqual(2, len(certs))
            self.assertTrue('milos 2013' in certs)
            self.assertTrue('My 2013 vacation' in certs)
            c = certs['My 2013 vacation'].keys[1]
            self.assertTrue(hasattr(c, 'key'))
            self.assertTrue(hasattr(c, 'method'))
            self.assertTrue(hasattr(c, 'input'))
            self.assertEqual(dummykey, c.input)
            self.assertEqual(1, c.key)
            self.assertEqual('pbkdf2', c.method)

    def test_links(self):
        with _temp_home() as home:
            cache = self._makeit(home)
            cdir = os.path.join(home, 'archives')
            os.makedirs(cdir)
            copy(os.path.join(self.home, 'archives', 'minimal.adf'), cdir)
            links = cache.links()
            self.assertEqual(1, len(links))
            self.assertTrue('milos 2013' in links)
            self.assertEqual(dummyurl, links['milos 2013'].download)
            copy(os.path.join(self.home, 'archives', 'sample.adf'), cdir)
            links = cache.links()
            self.assertEqual(2, len(links))
            self.assertTrue('milos 2013' in links)
            self.assertTrue('My 2013 vacation' in links)
            self.assertEqual(dummyurl, links['milos 2013'].download)
            self.assertEqual(dummyurl, links['My 2013 vacation'].download)
            self.assertEqual("file:///path/to/archive",
                             links['My 2013 vacation'].local)
