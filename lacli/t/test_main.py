import os
import shutil

from tempfile import mkdtemp
from testtools import TestCase
from mock import patch
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

    def test_home(self):
        settings = self._makeit()
        _, cache = settings({'--home': self.home})
        self.assertEqual(self.home, cache.home)

    @patch('lacli.main.sys.stdin', new_callable=StringIO)
    def test_make_no_home(self, stdin):
        try:
            settings = self._makeit()
            settings({
                '--batch': True,
                '--home': None
            })
        except SystemExit as e:
            self.assertEqual("None does not exist!", e.message)

        try:
            stdin.write("no\n")
            settings = self._makeit()
            settings({
                '--batch': True,
                '--home': None
            })
        except SystemExit as e:
            self.assertEqual("None does not exist!", e.message)

    @patch('lacli.main.sys.stdin', new_callable=StringIO)
    def test_make_home(self, stdin):
        try:
            tmpdir = mkdtemp()
            tmphome = os.path.join(tmpdir, 'a')
            stdin.write("yes\n")
            stdin.seek(0)
            settings = self._makeit()
            _, cache = settings({'--home': tmphome})
            self.assertEqual(tmphome, cache.home)
            self.assertTrue(os.path.isdir(tmphome))
        finally:
            if (tmpdir and os.path.isdir(tmphome)):
                shutil.rmtree(tmpdir)

    @patch('lacli.main.get_client_info')
    def test_user_agent(self, info):
        settings = self._makeit()
        info.return_value = self.getUniqueString()
        prefs, _ = settings({'--home': self.home})
        self.assertIn('api', prefs)
        self.assertIn('user_agent', prefs['api'])
        self.assertEqual(info.return_value, prefs['api']['user_agent'])
