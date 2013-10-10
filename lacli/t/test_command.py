import os
import time

from testtools import TestCase
from testtools.matchers import Contains
from . import makeprefs
from mock import Mock, patch
from contextlib import nested
from StringIO import StringIO


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

    def _makeupload(self, *args, **kwargs):
        return Mock(upload=Mock(**kwargs))

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

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_no_title(self, mock_stdout):
        cache = Mock(prepare=Mock(return_value='True'))
        cli = self._makeit(Mock(), cache, self.prefs)
        with cli.temp_var(archive_title=None):
            cli.onecmd('archive ' + self.home)
        cache.prepare.assert_called_with(
            time.strftime("%x archive"), self.home)
        self.assertThat(mock_stdout.getvalue(),
                        Contains('archive prepared'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_with_title(self, mock_stdout):
        cache = Mock(prepare=Mock(return_value='True'))
        cli = self._makeit(Mock(), cache, self.prefs)
        with cli.temp_var(archive_title='baz'):
            cli.onecmd('archive ' + self.home)
        cache.prepare.assert_called_with("baz", self.home)
        self.assertThat(mock_stdout.getvalue(),
                        Contains('archive prepared'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_exception(self, mock_stdout):
        cache = Mock(prepare=Mock(side_effect=Exception("foo")))
        cli = self._makeit(Mock(), cache, self.prefs)
        with cli.temp_var(archive_title='bar'):
            cli.onecmd('archive ' + self.home)
        self.assertThat(mock_stdout.getvalue(),
                        Contains('error: foo'))

    @patch('sys.stdin', new_callable=StringIO)
    def test_loop_none(self, mock_stdin):
        cli = self._makeit(Mock(), Mock, self.prefs)
        cli.cmdloop()

    def test_do_put_error(self):
        # cache = Mock(prepare=Mock(side_effect=Exception("foo")))
        cli = self._makeit(Mock(), Mock(), self.prefs)
        with patch('sys.stdout', new_callable=StringIO) as out:
            cli.onecmd('put')
            self.assertThat(out.getvalue(),
                            Contains('Argument required'))
        with patch('sys.stdout', new_callable=StringIO) as out:
            cli.onecmd('put /tmp/doesnotexistisaid')
            self.assertThat(out.getvalue(),
                            Contains('File /tmp/doesnotexistisaid not found.'))

    def test_do_put_done(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            cli = self._makeit(Mock(), Mock(), self.prefs, Mock())
            cli.onecmd('put t/data/arc1')
            self.assertThat(out.getvalue(),
                            Contains('done'))

    def test_do_put_exception(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            cli = self._makeit(Mock(), Mock(), self.prefs,
                               self._makeupload(side_effect=Exception))
            cli.onecmd('put t/data/arc1')
            self.assertThat(out.getvalue(),
                            Contains('error:'))

    def test_do_restore(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            cli = self._makeit(Mock(), Mock(), self.prefs, Mock())
            cli.onecmd('restore')
            self.assertThat(out.getvalue(), Contains('No available archive'))
            cli.onecmd('restore 1')
            self.assertThat(out.getvalue(), Contains('No such archive'))
