import os

from testtools import TestCase
from . import makeprefs
from mock import Mock


class RegistryTest(TestCase):
    def setUp(self):
        super(RegistryTest, self).setUp()
        self.prefs = makeprefs(lambda x: None)
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(RegistryTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.registry import LaRegistry
        return LaRegistry(*args, **kwargs)

    def test_registry(self):
        assert self._makeit(Mock(), self.prefs, Mock())
