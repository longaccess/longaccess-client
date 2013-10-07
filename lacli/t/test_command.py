import os

from testtools import TestCase
from . import makeprefs
from mock import Mock


class CommandTest(TestCase):
    def setUp(self):
        super(CommandTest, self).setUp()
        self.prefs = makeprefs()
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(CommandTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.command import LaCommand
        return LaCommand(*args, **kwargs)

    def test_command(self):
        assert self._makeit(Mock(), Mock(), self.prefs)

    def test_temp_var(self):
        cli = self._makeit(Mock(), Mock(), self.prefs)
        cli._var['foo'] = 'ham'
        cli._default_var['none'] = 'some'
        cli._default_var['acid'] = lambda: "funk"
        with cli.temp_var(foo='spam', bar='baz', none=None, acid=None):
            self.assertEqual(cli._var['foo'], 'spam')
            self.assertEqual(cli._var['bar'], 'baz')
            self.assertEqual(cli._var['none'], 'some')
            self.assertEqual(cli._var['acid'], 'funk')
        self.assertEqual(cli._var['foo'], 'ham')
        assert 'bar' not in cli._var
        assert 'none' not in cli._var
        assert 'acid' not in cli._var
