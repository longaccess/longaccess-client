import os

from testtools import TestCase
from testtools.matchers import Contains
from . import makeprefs
from mock import Mock, patch
from StringIO import StringIO
from twisted.internet import defer


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
        assert self._makeit(Mock(), makeprefs(Mock()))

    @patch('sys.stdin', new_callable=StringIO)
    def test_loop_none(self, mock_stdin):
        factory = Mock()
        factory.return_value.async_account = defer.succeed(
            {'email': 'foo'})
        cli = self._makeit(Mock(), makeprefs(factory))
        cli.cmdloop()

    @patch('sys.stdout', new_callable=StringIO)
    def test_dispatch(self, stdout):
        cli = self._makeit(Mock(), makeprefs(Mock()))
        cli.dispatch('foo', [])
        self.assertThat(stdout.getvalue(),
                        Contains('Unrecognized command: foo'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_dispatch_foo(self, stdout):
        cli = self._makeit(Mock(), makeprefs(Mock()))
        with patch.object(cli, 'foo', create=True) as foo:
            foo.__doc__ = "Usage: lacli foo"
            foo.makecmd.return_value = 'bar'
            cli.dispatch('foo', [])
            self.assertEqual('', stdout.getvalue())
            foo.onecmd.assert_called_with('bar')

    @patch('sys.stdout', new_callable=StringIO)
    def test_dispatch_login(self, stdout):
        factory = Mock()
        factory.return_value.async_account = defer.succeed(
            {'email': 'foo'})
        cli = self._makeit(Mock(), makeprefs(factory))

        cli.dispatch('login', [])
        self.assertThat(stdout.getvalue(),
                        Contains('authentication succesfull'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_login(self, stdout):
        factory = Mock()
        factory.return_value.async_account = defer.succeed(
            {'email': 'foo'})
        cli = self._makeit(Mock(), makeprefs(factory))
        cli.onecmd('login')
        self.assertThat(stdout.getvalue(),
                        Contains('authentication succesfull'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_login_with_creds(self, stdout):
        factory = Mock()
        factory.return_value.async_account = defer.succeed(
            {'email': 'foo'})
        cli = self._makeit(Mock(), makeprefs(factory))
        cli.onecmd('login username password')
        self.assertThat(stdout.getvalue(),
                        Contains('authentication succesfull'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_login_with_bad_creds(self, stdout):
        factory = Mock()
        factory.return_value.async_account = defer.fail(
            Exception())

        cli = self._makeit(Mock(), makeprefs(factory))
        cli.onecmd('login username password')
        self.assertThat(stdout.getvalue(),
                        Contains('authentication failed'))
