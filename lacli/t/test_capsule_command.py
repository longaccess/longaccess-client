import os

from . import makeprefs
from testtools import TestCase
from mock import Mock, patch
from StringIO import StringIO


class CapsuleCommandTest(TestCase):
    def setUp(self):
        super(CapsuleCommandTest, self).setUp()
        self.prefs = makeprefs()
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(CapsuleCommandTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.command import LaCapsuleCommand
        return LaCapsuleCommand(*args, **kwargs)

    def _makeupload(self, *args, **kwargs):
        return Mock(upload=Mock(**kwargs))

    def test_command(self):
        assert self._makeit(Mock(), Mock(), self.prefs)

    def test_do_list_exception(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            s = Mock(capsules=Mock(side_effect=Exception("foo")))
            cli = self._makeit(s, Mock(), self.prefs)
            cli.onecmd('list')
            self.assertEqual("error: foo\n", out.getvalue())

    def test_list_capsules(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            s = Mock(capsules=Mock(return_value=()))
            cli = self._makeit(s, Mock(), self.prefs)
            cli.onecmd('list')
            self.assertEqual("No available capsules.\n", out.getvalue())

    def test_list_capsules_some(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            s = Mock(capsules=Mock(return_value=({'title': 'foo', 'a': 'b'},)))
            cli = self._makeit(s, Mock(), self.prefs)
            cli.onecmd('list')
            r = '''\
Available capsules:
title     :       foo
a         :         b


'''
            self.assertEqual(r, out.getvalue())
