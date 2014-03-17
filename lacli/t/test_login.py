import os

from testtools import TestCase
from testtools.matchers import Contains
from . import makeprefs
from mock import Mock, patch
from StringIO import StringIO
from twisted.internet import defer


class LoginCommandTest(TestCase):
    def setUp(self):
        super(LoginCommandTest, self).setUp()
        self.prefs = makeprefs()
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(LoginCommandTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.main import LaLoginCommand
        return LaLoginCommand(*args, **kwargs)

    def test_login_command(self):
        assert self._makeit(Mock(), Mock(), self.prefs)

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_login(self, stdout):
        registry = Mock()
        registry.prefs = self.prefs
        registry.new_session.return_value.async_account = defer.succeed(
            {'email': 'foo'})
        cli = self._makeit(registry)

        cli.onecmd('login')
        self.assertThat(stdout.getvalue(),
                        Contains('authentication succesfull'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_login_user(self, stdout):
        registry = Mock()
        registry.prefs = self.prefs
        registry.new_session.return_value.async_account = defer.succeed(
            {'email': 'foo'})
        cli = self._makeit(registry)

        cli.onecmd('login user pass')
        self.assertThat(stdout.getvalue(),
                        Contains('authentication succesfull as foo'))
        self.assertEqual('user', cli.username)
        self.assertEqual('pass', cli.password)
        self.assertEqual('foo', cli.email)

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_logout_user(self, stdout):
        registry = Mock()
        registry.prefs = self.prefs
        registry.new_session.return_value.async_account = defer.succeed(
            {'email': 'foo'})
        cli = self._makeit(registry)

        cli.onecmd('login user pass')
        self.assertThat(stdout.getvalue(),
                        Contains('authentication succesfull as foo'))
        self.assertEqual('user', cli.username)
        self.assertEqual('pass', cli.password)
        self.assertEqual('foo', cli.email)
        cli.onecmd('logout')
        self.assertEqual(None, cli.username)
        self.assertEqual(None, cli.password)
        self.assertEqual(None, cli.email)
        self.assertEqual(None, cli.registry.session)

    def test_do_logout(self):
        registry = Mock()
        registry.prefs = self.prefs
        registry.session = "foobar"
        cli = self._makeit(registry)

        cli.onecmd('logout')
        self.assertEqual(None, cli.registry.session)

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_login_session_fail(self, stdout):
        registry = Mock()
        registry.prefs = self.prefs
        registry.new_session.side_effect = Exception()
        cli = self._makeit(registry)

        cli.onecmd('login')
        self.assertThat(stdout.getvalue(),
                        Contains('authentication failed'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_login_auth_fail(self, stdout):
        registry = Mock()
        registry.prefs = self.prefs
        registry.new_session.return_value.async_account = defer.fail(
            Exception())
        cli = self._makeit(registry)

        cli.onecmd('login')
        self.assertThat(stdout.getvalue(),
                        Contains('authentication failed'))

    def test_makecmd(self):
        cli = self._makeit(Mock())
        self.assertEqual(
            "login foo bar",
            cli.makecmd({'<username>': 'foo', '<password>': 'bar'}))
