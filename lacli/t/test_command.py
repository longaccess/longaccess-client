import os

from testtools import TestCase
from testtools.matchers import Contains
from . import makeprefs
from mock import Mock, patch
from StringIO import StringIO


class CommandTest(TestCase):
    def setUp(self):
        super(CommandTest, self).setUp()
        self.prefs = makeprefs()
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(CommandTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.main import LaCommand
        return LaCommand(*args, **kwargs)

    def test_command(self):
        assert self._makeit(Mock(), Mock(), self.prefs)

    @patch('sys.stdin', new_callable=StringIO)
    def test_loop_none(self, mock_stdin):
        cli = self._makeit(Mock(), Mock, self.prefs)
        cli.cmdloop()

    @patch('sys.stdout', new_callable=StringIO)
    def test_dispatch(self, stdout):
        cli = self._makeit(Mock(), Mock, self.prefs)
        cli.dispatch('foo', [])
        self.assertThat(stdout.getvalue(),
                        Contains('Unrecognized command: foo'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_dispatch_foo(self, stdout):
        cli = self._makeit(Mock(), Mock, self.prefs)
        with patch.object(cli, 'foo', create=True) as foo:
            foo.__doc__ = "Usage: lacli foo"
            foo.makecmd.return_value = 'bar'
            cli.dispatch('foo', [])
            self.assertEqual('', stdout.getvalue())
            foo.onecmd.assert_called_with('bar')

    @patch('sys.stdout', new_callable=StringIO)
    def test_dispatch_login(self, stdout):
        cli = self._makeit(Mock(), Mock, self.prefs)

        cli.dispatch('login', [])
        self.assertThat(stdout.getvalue(),
                        Contains('logged in'))
