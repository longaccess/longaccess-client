# -*- coding: utf-8 -*-
import os

from testtools import TestCase
from . import makeprefs
from shutil import rmtree
from contextlib import contextmanager
from tempfile import mkdtemp
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

    @contextmanager
    def _temp_home(self):
        d = mkdtemp()
        yield d
        rmtree(d)

    def test_cache(self):
        assert self._makeit("")

    def test_archives_empty(self):
        self.assertEqual(self._makeit("doesnotexist").archives(), [])

    def test_archives(self):
        archives = self._makeit(self.home).archives()
        self.assertEqual(len(archives), 2)
        self.assertEqual(archives[0].title, 'milos 2013')

    def test_slugify(self):
        from lacli.cache import Cache
        self.assertEqual(Cache._slugify("This is a test"), "this-is-a-test")
        self.assertEqual(Cache._slugify(u"γειά σου ρε"), "geia-sou-re")

    def test_prepare(self):
        with self._temp_home() as home:
            cache = self._makeit(home)
            cache.prepare('foo', os.path.join('t', 'data', 'arc1'))
            archives = cache.archives()
            self.assertEqual(len(archives), 1)
            self.assertEqual(archives[0].title, 'foo')

    def test_cache_dir(self):
        d = 'archives'
        self.assertTrue(
            os.path.isdir(self._makeit(self.home)._cache_dir(d)))
        with self._temp_home() as home:
            cache = self._makeit(home)
            self.assertFalse(os.path.exists(cache._cache_dir(d)))
            self.assertTrue(os.path.isdir(cache._cache_dir(d, write=True)))

    def test_archive_open(self):
        open_mock = Mock(return_value=None)
        import lacli.cache as cache
        with patch.object(cache, 'open', open_mock, create=True):
            with self._temp_home() as home:
                cache = self._makeit(home)
                dname = os.path.join(home, 'archives')
                fname = os.path.join(dname, 'foo')
                cache._archive_open('foo', 'w')
                open_mock.assert_called_with(fname, 'w')
                self.assertTrue(os.path.isdir(dname))
