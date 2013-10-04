from testtools import TestCase
from . import makeprefs


class CacheTest(TestCase):
    def setUp(self):
        super(CacheTest, self).setUp()
        self.prefs = makeprefs()

    def tearDown(self):
        super(CacheTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.cache import Cache
        return Cache(*args, **kwargs)

    def test_cache(self):
        assert self._makeit("")

    def test_archives(self):
        self.assertEqual(self._makeit("").archives(), [])
