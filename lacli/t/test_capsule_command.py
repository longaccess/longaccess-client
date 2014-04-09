import os

from . import makeprefs, dummycapsule
from testtools import TestCase
from testtools.matchers import Contains
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
            registry = Mock()
            registry.prefs = self.prefs
            registry.session.capsules.side_effect = Exception("foo")
            cli = self._makeit(registry)
            cli.onecmd('list')
            self.assertEqual("error: foo\n", out.getvalue())

    def test_list_capsules(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            registry = Mock()
            registry.prefs = self.prefs
            registry.session.capsules.return_value = ()
            cli = self._makeit(registry)
            cli.onecmd('list')
            self.assertEqual("No available capsules.\n", out.getvalue())

    def test_list_capsules_some(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            registry = Mock()
            registry.prefs = self.prefs

            registry.session.capsules.return_value = (dummycapsule,)
            cli = self._makeit(registry)
            cli.onecmd('list')
            self.assertThat(out.getvalue(),
                            Contains('foo'))
            self.assertThat(out.getvalue(),
                            Contains('bar'))
            self.assertThat(out.getvalue(),
                            Contains('1 MB'))
            self.assertThat(out.getvalue(),
                            Contains('1970-01-01'))
