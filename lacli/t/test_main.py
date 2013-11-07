import os

from testtools import TestCase
from testtools.matchers import Contains
from . import makeprefs
from mock import Mock, patch
from StringIO import StringIO


class SettingsTest(TestCase):
    def setUp(self):
        super(SettingsTest, self).setUp()
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(SettingsTest, self).tearDown()

    def _makeit(self):
        from lacli.main import settings
        return settings

    def test_settings(self):
        settings = self._makeit()
        settings({})

