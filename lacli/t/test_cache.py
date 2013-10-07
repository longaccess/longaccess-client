# -*- coding: utf-8 -*-
import os

from testtools import TestCase
from . import makeprefs


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
        self.assertEqual(len(archives), 1)
        self.assertEqual(archives[0].title, 'milos 2013')

    def test_slugify(self):
        from lacli.cache import Cache
        self.assertEqual(Cache._slugify("This is a test"), "this-is-a-test")
        self.assertEqual(Cache._slugify(u"γειά σου ρε"), "geia-sou-re")
