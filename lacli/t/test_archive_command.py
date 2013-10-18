import os

from testtools import TestCase
from testtools.matchers import Contains
from . import makeprefs, _temp_home
from mock import MagicMock, Mock, patch
from StringIO import StringIO
from contextlib import nested


class ArchiveCommandTest(TestCase):
    def setUp(self):
        super(ArchiveCommandTest, self).setUp()
        self.prefs = makeprefs()
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(ArchiveCommandTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.main import LaArchiveCommand
        return LaArchiveCommand(*args, **kwargs)

    def _makeupload(self, *args, **kwargs):
        return Mock(upload=Mock(**kwargs))

    def test_command(self):
        assert self._makeit(Mock(), Mock(), self.prefs)

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_with_title(self, mock_stdout):
        cache = Mock(prepare=Mock(return_value='True'))
        cli = self._makeit(Mock(), cache, self.prefs)
        cli.onecmd('create {} baz'.format(self.home))
        cache.prepare.assert_called_with("baz", self.home)
        self.assertThat(mock_stdout.getvalue(),
                        Contains('archive prepared'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_exception(self, mock_stdout):
        cache = Mock(prepare=Mock(side_effect=Exception("foo")))
        cli = self._makeit(Mock(), cache, self.prefs)
        cli.onecmd('create {} baz'.format(self.home))
        self.assertThat(mock_stdout.getvalue(),
                        Contains('error: foo'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_unexist(self, mock_stdout):
        cli = self._makeit(Mock(), Mock(), self.prefs)
        cli.onecmd('create /tmp/doesnotexistisay foo')
        self.assertEqual('The specified folder does not exist.\n',
                         mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_list_none(self, out):
        cache = Mock(_for_adf=Mock(return_value=[]))
        cli = self._makeit(Mock(), cache, self.prefs)
        cli.onecmd('list')
        self.assertEqual('No available archives.\n', out.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_list_some(self, out):
        from lacli.adf import Archive, Meta
        meta = Meta(format='', size=None, cipher='')
        archive = Archive(title="foo", description='',
                          tags=[], meta=meta)
        cache = Mock(_for_adf=Mock(
            return_value={'foo': {'archive': archive}}))
        cli = self._makeit(Mock(), cache, self.prefs)
        cli.onecmd('list')
        self.assertThat(out.getvalue(),
                        Contains('Prepared archives:\n1) foo'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_list_verbose(self, out):
        from lacli.adf import Archive, Meta
        meta = Meta(format='', size=None, cipher='')
        archive = Archive(title="foo", description='',
                          tags=[], meta=meta)
        cache = Mock(_for_adf=Mock(
            return_value={'foo': {'archive': archive}}))
        prefs = self.prefs
        prefs['command']['verbose'] = True
        cli = self._makeit(Mock(), cache, self.prefs)
        cli.onecmd('list')
        self.assertThat(out.getvalue(),
                        Contains('!archive'))

    def test_do_archive_list_more(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            for size in [(25, '25B'), (1024, '1KiB'), (2000000, '1MiB')]:
                from lacli.adf import Archive, Meta
                meta = Meta(format='', size=size[0], cipher='')
                archive = Archive(title="foo", description='',
                                  tags=[], meta=meta)
                cache = Mock(_for_adf=Mock(
                    return_value={'foo': {'archive': archive}}))
                cli = self._makeit(Mock(), cache, self.prefs)
                cli.onecmd('list')
                self.assertThat(out.getvalue(),
                                Contains('Prepared archives:\n1) foo [//'
                                         + size[1]))

    @patch('sys.stdin', new_callable=StringIO)
    def test_loop_none(self, mock_stdin):
        cli = self._makeit(Mock(), Mock, self.prefs)
        cli.cmdloop()

    def test_do_status_error(self):
        from lacli.cache import Cache
        cli = self._makeit(Mock(), Cache(self.home), self.prefs)
        with patch('sys.stdout', new_callable=StringIO) as out:
            cli.onecmd('status foobar')
            self.assertThat(out.getvalue(),
                            Contains('error: invalid value'))
        apisession = Mock()
        apisession.upload_status.side_effect = Exception('foo')
        cli = self._makeit(apisession, Cache(self.home), self.prefs)
        with nested(
            patch('sys.stdout', new_callable=StringIO),
            patch('lacli.command.urlparse'),
                ) as (out, urlparse):
            uploads = cli.cache._for_adf('archives')
            urlparse.return_value = Mock(scheme='gopher', path=self.home)
            for seq, archive in enumerate(uploads.itervalues()):
                    if archive['archive'].title == 'My pending upload':
                        cli.onecmd('status {}'.format(seq+1))
            self.assertThat(out.getvalue(),
                            Contains('error:'))

    def test_do_status(self):
        from lacli.cache import Cache
        cli = self._makeit(Mock(), Cache(self.home), self.prefs)
        with patch('sys.stdout', new_callable=StringIO) as out:
            cli.onecmd('status')
            self.assertThat(out.getvalue(),
                            Contains('Usage:'))

    def test_do_put_error(self):
        from lacli.cache import Cache
        with _temp_home() as home:
            cli = self._makeit(Mock(), Cache(home), self.prefs)
            with patch('sys.stdout', new_callable=StringIO) as out:
                cli.onecmd('upload')
                self.assertThat(out.getvalue(),
                                Contains('No such archive'))
        cli = self._makeit(Mock(), Cache(self.home), self.prefs)
        with patch('sys.stdout', new_callable=StringIO) as out:
            cli.onecmd('upload foobar')
            self.assertThat(out.getvalue(),
                            Contains('error: invalid value'))
        with patch('sys.stdout', new_callable=StringIO) as out:
            archives = cli.cache._for_adf('archives')
            for seq, archive in enumerate(archives.itervalues()):
                if archive['archive'].title == 'My 2013 vacation':
                    cli.onecmd('upload {}'.format(seq+1))
            self.assertThat(out.getvalue(),
                            Contains('upload is already completed'))

    def test_do_put_not_found(self):
        from lacli.cache import Cache
        cli = self._makeit(Mock(), Cache(self.home), self.prefs)
        cli.cache.links = Mock(return_value={})
        with patch('sys.stdout', new_callable=StringIO) as out:
            for seq, archive in enumerate(cli.cache._for_adf('archives')):
                if archive.title == 'My 2013 vacation':
                    cli.onecmd('upload {}'.format(seq+1))
            self.assertThat(out.getvalue(), Contains('no local copy exists'))

    def test_do_put_not_local(self):
        from lacli.cache import Cache
        cli = self._makeit(Mock(), Cache(self.home), self.prefs)
        with patch('sys.stdout', new_callable=StringIO) as out:
            with patch('lacli.command.urlparse') as urlparse:
                urlparse.return_value = Mock(scheme='gopher', path=self.home)
                for seq, archive in enumerate(cli.cache._for_adf('archives')):
                    if archive.title == 'My 2013 vacation':
                        cli.onecmd('upload {}'.format(seq+1))
                self.assertThat(out.getvalue(), Contains('url not local'))
                urlparse.assert_called_with('file:///path/to/archive')

    def test_do_put_done(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            from lacli.cache import Cache
            upload = MagicMock()
            upload.__enter__.return_value = {
                'uri': 'http://foo.com',
                'id': '1',
                'tokens': Mock()
            }
            with patch.object(Cache, 'save_upload'):
                cli = self._makeit(Mock(upload=Mock(return_value=upload)),
                                   Cache(self.home),
                                   self.prefs,
                                   self._makeupload())
                with patch('lacli.command.urlparse') as urlparse:
                    urlparse.return_value = Mock(scheme='file', path=self.home)
                    archives = cli.cache._for_adf('archives')
                    for seq, archive in enumerate(archives):
                        if archive.title == 'My 2013 vacation':
                            cli.onecmd('upload {}'.format(seq+1))
            self.assertThat(out.getvalue(), Contains('done'))

    def test_do_put_exception(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            from lacli.cache import Cache
            upload = MagicMock()
            upload.__enter__.return_value = {
                'uri': 'http://foo.com',
                'id': '1',
                'tokens': Mock()
            }
            cli = self._makeit(Mock(upload=Mock(return_value=upload)),
                               Cache(self.home), self.prefs,
                               self._makeupload(side_effect=Exception))
            with patch('lacli.command.urlparse') as urlparse:
                urlparse.return_value = Mock(scheme='file', path=self.home)
                for seq, archive in enumerate(cli.cache._for_adf('archives')):
                    if archive.title == 'My 2013 vacation':
                        cli.onecmd('upload {}'.format(seq+1))
            self.assertThat(out.getvalue(),
                            Contains('error:'))

    def test_do_restore_none(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            cache = Mock(archives=Mock(return_value=[]))
            cli = self._makeit(Mock(), cache, self.prefs, Mock())
            cli.onecmd('extract')
            self.assertThat(out.getvalue(), Contains('No such archive'))
            cli.onecmd('restore 1')
            self.assertThat(out.getvalue(), Contains('No such archive'))
            cli.onecmd('restore foobar')
            self.assertThat(out.getvalue(), Contains('No such archive'))

    @patch('lacli.command.restore_archive')
    def test_do_restore(self, restore_archive):
        with patch('sys.stdout', new_callable=StringIO) as out:
            cache = Mock(archives=Mock(return_value=[Mock(title='foo')]),
                         certs=Mock(return_value={}),
                         links=Mock(return_value={}))
            cli = self._makeit(Mock(), cache, self.prefs, Mock())
            cli.onecmd('extract')
            self.assertThat(out.getvalue(),
                            Contains('no matching certificate found'))
        with patch('sys.stdout', new_callable=StringIO) as out:
            cache.certs.return_value = {'foo': 'cert'}
            cli.onecmd('extract')
            self.assertThat(out.getvalue(), Contains('no local copy exists'))
        with patch('sys.stdout', new_callable=StringIO) as out:
            cache.links.return_value = {'foo': Mock(local="file:///path")}
            with patch('lacli.command.urlparse') as urlparse:
                urlparse.return_value = Mock(scheme='gopher', path=self.home)
                cli.onecmd('extract')
                self.assertThat(out.getvalue(), Contains('url not local'))
        with patch('sys.stdout', new_callable=StringIO) as out:
            cache.links.return_value = {'foo': Mock(local="file:///path")}
            cli.onecmd('extract')
            self.assertThat(out.getvalue(), Contains('archive restored'))
        with patch('sys.stdout', new_callable=StringIO) as out:
            cache.links.return_value = {'foo': Mock(local="file:///path")}
            cli.onecmd('extract')
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
            cli.onecmd('extract')
            self.assertThat(out.getvalue(), Contains('error: foo'))

    @patch('sys.stdin', new_callable=StringIO)
    def test_do_archive(self, mock_stdin):
        cli = self._makeit(Mock(), Mock, self.prefs)
        cli.onecmd('archive')
