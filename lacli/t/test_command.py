import os
import time

from testtools import TestCase
from testtools.matchers import Contains
from . import makeprefs, _temp_home
from mock import MagicMock, Mock, patch
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

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_unexist(self, mock_stdout):
        cli = self._makeit(Mock(), Mock(), self.prefs)
        cli.onecmd('archive /tmp/doesnotexistisay')
        self.assertEqual('The specified folder does not exist.\n',
                         mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_list_none(self, out):
        cache = Mock(archives=Mock(return_value=[]))
        cli = self._makeit(Mock(), cache, self.prefs)
        cli.onecmd('archive')
        self.assertEqual('No prepared archives.\n', out.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_list_some(self, out):  # NOQA
        cache = Mock(archives=Mock(return_value=[
            Mock(title="foo", description='', tags=[], meta=Mock(format=''))]))
        cli = self._makeit(Mock(), cache, self.prefs)
        cli.onecmd('archive')
        self.assertThat(out.getvalue(),
                        Contains('Prepared archives:\n1) foo\n'))

    @patch('sys.stdin', new_callable=StringIO)
    def test_loop_none(self, mock_stdin):
        cli = self._makeit(Mock(), Mock, self.prefs)
        cli.cmdloop()

    def test_do_put_error(self):
        from lacli.cache import Cache
        with _temp_home() as home:
            cli = self._makeit(Mock(), Cache(home), self.prefs)
            with patch('sys.stdout', new_callable=StringIO) as out:
                cli.onecmd('put')
                self.assertThat(out.getvalue(),
                                Contains('No such archive'))
        cli = self._makeit(Mock(), Cache(self.home), self.prefs)
        with patch('sys.stdout', new_callable=StringIO) as out:
            cli.onecmd('put foobar')
            self.assertThat(out.getvalue(),
                            Contains('No such archive'))
        with patch('sys.stdout', new_callable=StringIO) as out:
            for seq, archive in enumerate(cli.cache.archives()):
                if archive.title == 'My 2013 vacation':
                    cli.onecmd('put {}'.format(seq+1))
            self.assertThat(out.getvalue(),
                            Contains('File /path/to/archive not found.'))

    def test_do_put_not_found(self):
        from lacli.cache import Cache
        cli = self._makeit(Mock(), Cache(self.home), self.prefs)
        cli.cache.links = Mock(return_value={})
        with patch('sys.stdout', new_callable=StringIO) as out:
            for seq, archive in enumerate(cli.cache.archives()):
                if archive.title == 'My 2013 vacation':
                    cli.onecmd('put {}'.format(seq+1))
            self.assertThat(out.getvalue(), Contains('no local copy exists'))

    def test_do_put_not_local(self):
        from lacli.cache import Cache
        cli = self._makeit(Mock(), Cache(self.home), self.prefs)
        with patch('sys.stdout', new_callable=StringIO) as out:
            with patch('lacli.command.urlparse') as urlparse:
                urlparse.return_value = Mock(scheme='gopher', path=self.home)
                for seq, archive in enumerate(cli.cache.archives()):
                    if archive.title == 'My 2013 vacation':
                        cli.onecmd('put {}'.format(seq+1))
                self.assertThat(out.getvalue(), Contains('url not local'))
                urlparse.assert_called_with('file:///path/to/archive')

    def test_do_put_done(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            from lacli.cache import Cache
            cli = self._makeit(Mock(upload=MagicMock()), Cache(self.home),
                               self.prefs, self._makeupload())
            cli._var['capsule'] = 1
            with patch('lacli.command.urlparse') as urlparse:
                urlparse.return_value = Mock(scheme='file', path=self.home)
                for seq, archive in enumerate(cli.cache.archives()):
                    if archive.title == 'My 2013 vacation':
                        cli.onecmd('put {}'.format(seq+1))
            self.assertThat(out.getvalue(), Contains('done'))

    def test_do_put_exception(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            from lacli.cache import Cache
            cli = self._makeit(Mock(), Cache(self.home), self.prefs,
                               self._makeupload(side_effect=Exception))
            with patch('lacli.command.urlparse') as urlparse:
                urlparse.return_value = Mock(scheme='file', path=self.home)
                for seq, archive in enumerate(cli.cache.archives()):
                    if archive.title == 'My 2013 vacation':
                        cli.onecmd('put {}'.format(seq+1))
            self.assertThat(out.getvalue(),
                            Contains('error:'))

    def test_do_restore_none(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            cache = Mock(archives=Mock(return_value=[]))
            cli = self._makeit(Mock(), cache, self.prefs, Mock())
            cli.onecmd('restore')
            self.assertThat(out.getvalue(), Contains('No such archive'))
            cli.onecmd('restore 1')
            self.assertThat(out.getvalue(), Contains('No such archive'))

    @patch('lacli.command.restore_archive')
    def test_do_restore(self, restore_archive):
        with patch('sys.stdout', new_callable=StringIO) as out:
            cache = Mock(archives=Mock(return_value=[Mock(title='foo')]),
                         certs=Mock(return_value={}),
                         links=Mock(return_value={}))
            cli = self._makeit(Mock(), cache, self.prefs, Mock())
            cli.onecmd('restore')
            self.assertThat(out.getvalue(),
                            Contains('no matching certificate found'))
        with patch('sys.stdout', new_callable=StringIO) as out:
            cache.certs.return_value = {'foo': 'cert'}
            cli.onecmd('restore')
            self.assertThat(out.getvalue(), Contains('no local copy exists'))
        with patch('sys.stdout', new_callable=StringIO) as out:
            cache.links.return_value = {'foo': Mock(local="file:///path")}
            with patch('lacli.command.urlparse') as urlparse:
                urlparse.return_value = Mock(scheme='gopher', path=self.home)
                cli.onecmd('restore')
                self.assertThat(out.getvalue(), Contains('url not local'))
        with patch('sys.stdout', new_callable=StringIO) as out:
            cache.links.return_value = {'foo': Mock(local="file:///path")}
            cli.onecmd('restore')
            self.assertThat(out.getvalue(), Contains('archive restored'))
        with patch('sys.stdout', new_callable=StringIO) as out:
            cache.links.return_value = {'foo': Mock(local="file:///path")}
            cli._var['output_directory'] = 'foo'
            cli.onecmd('restore')
            self.assertThat(out.getvalue(), Contains('archive restored'))
            args, kwargs = restore_archive.call_args
            a, p, cert, o, c, cb = args
            self.assertEqual('cert', cert)
            self.assertEqual('/path', p)
            self.assertEqual('foo', o)
            cb("foo")
            self.assertThat(out.getvalue(), Contains("Extracting foo"))
        with patch('sys.stdout', new_callable=StringIO) as out:
            restore_archive.side_effect = Exception("foo")
            cache.links.return_value = {'foo': Mock(local="file:///path")}
            cli._var['output_directory'] = 'foo'
            cli.onecmd('restore')
            self.assertThat(out.getvalue(), Contains('error: foo'))

    def test_do_list_exception(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            s = Mock(capsules=Mock(side_effect=Exception("foo")))
            cli = self._makeit(s, Mock(), self.prefs, Mock())
            cli.onecmd('list')
            self.assertEqual("error: foo\n", out.getvalue())

    def test_list_capsules(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            s = Mock(capsules=Mock(return_value=()))
            cli = self._makeit(s, Mock(), self.prefs, Mock())
            cli.onecmd('list')
            self.assertEqual("No available capsules.\n", out.getvalue())

    def test_list_capsules_some(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            s = Mock(capsules=Mock(return_value=({'title': 'foo', 'a': 'b'},)))
            cli = self._makeit(s, Mock(), self.prefs, Mock())
            cli.onecmd('list')
            r = '''\
Available capsules:
title     :       foo
a         :         b


'''
            self.assertEqual(r, out.getvalue())
