import os

from testtools import TestCase
from testtools.matchers import Contains
from . import makeprefs
from mock import Mock, patch
from StringIO import StringIO


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
        cli = self._makeit(Mock(), Mock, self.prefs)

        cli.onecmd('login')
        self.assertThat(stdout.getvalue(),
                        Contains('authentication succesfull'))
