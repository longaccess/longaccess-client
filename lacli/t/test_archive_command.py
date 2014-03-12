import os

from testtools import TestCase
from testtools.matchers import Contains
from . import makeprefs, _temp_home
from mock import Mock, patch
from StringIO import StringIO


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
        assert self._makeit(Mock(prefs=self.prefs))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_with_title(self, mock_stdout):
        registry = Mock()
        registry.cache.prepare.return_value = True
        registry.prefs = self.prefs
        cli = self._makeit(registry)
        cli.onecmd('create {} baz'.format(self.home))
        args, _ = registry.cache.prepare.call_args
        self.assertTrue(self.home in args)
        self.assertTrue(u'baz' in args)
        self.assertThat(mock_stdout.getvalue(),
                        Contains('archive prepared'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_exception(self, mock_stdout):
        registry = Mock()
        registry.cache.prepare.side_effect = Exception("foo")
        registry.prefs = self.prefs
        cli = self._makeit(registry)
        cli.onecmd('create {} baz'.format(self.home))
        self.assertThat(mock_stdout.getvalue(),
                        Contains('error: foo'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_unexist(self, mock_stdout):
        cli = self._makeit(Mock(prefs=self.prefs))
        cli.onecmd('create /tmp/doesnotexistisay foo')
        self.assertEqual('The specified folder does not exist.\n',
                         mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_list_none(self, out):
        registry = Mock()
        registry.cache._for_adf.return_value = {}
        cli = self._makeit(registry, self.prefs)
        cli.onecmd('list')
        self.assertEqual('No available archives.\n', out.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_list_some(self, out):
        from lacli.adf import Archive, Meta
        meta = Meta(format='', size=None, cipher='')
        archive = Archive(title="foo", description='',
                          tags=[], meta=meta)
        registry = Mock()
        registry.cache._for_adf.return_value = {'foo': {'archive': archive}}
        registry.prefs = self.prefs
        cli = self._makeit(registry)
        cli.onecmd('list')
        self.assertThat(out.getvalue(),
                        Contains('foo'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_do_archive_list_debug(self, out):
        from lacli.adf import Archive, Meta
        meta = Meta(format='', size=None, cipher='')
        archive = Archive(title="foo", description='',
                          tags=[], meta=meta)
        registry = Mock()
        registry.cache._for_adf.return_value = {'foo': {'archive': archive}}
        registry.prefs = self.prefs
        registry.prefs['command']['debug'] = 3
        cli = self._makeit(registry)
        cli.onecmd('list')
        self.assertThat(out.getvalue(),
                        Contains('!archive'))

    def test_do_archive_list_more(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            for size in [(25, '25 B'), (1024, '1 KB'), (2000000, '1 MB')]:
                from lacli.adf import Archive, Meta
                meta = Meta(format='', size=size[0], cipher='')
                archive = Archive(title="foo", description='',
                                  tags=[], meta=meta)
                registry = Mock()
                registry.cache._for_adf.return_value = {
                    'foo': {'archive': archive}}
                registry.prefs = self.prefs
                cli = self._makeit(registry)
                cli.onecmd('list')
                self.assertThat(out.getvalue(),
                                Contains('foo'))
                self.assertThat(out.getvalue(),
                                Contains(size[1]))

    @patch('sys.stdin', new_callable=StringIO)
    def test_loop_none(self, mock_stdin):
        cli = self._makeit(Mock(prefs=self.prefs))
        cli.cmdloop()

    def test_do_status(self):
        from lacli.cache import Cache
        registry = Mock()
        registry.cache = Cache(self.home)
        with patch('sys.stdout', new_callable=StringIO) as out:
            cli = self._makeit(registry, self.prefs)
            cli.onecmd('status')
            self.assertThat(out.getvalue(),
                            Contains('Usage:'))

    def test_do_put_error(self):
        from lacli.cache import Cache
        with _temp_home() as home:
            registry = Mock()
            registry.cache = Cache(home)
            cli = self._makeit(registry, self.prefs)
            with patch('sys.stdout', new_callable=StringIO) as out:
                cli.onecmd('upload')
                self.assertThat(out.getvalue(),
                                Contains('no such archive'))
        registry = Mock()
        registry.cache = Cache(home)
        cli = self._makeit(registry, self.prefs)
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
        registry = Mock()
        registry.cache = Cache(self.home)
        registry.cache.links = Mock(return_value={})
        cli = self._makeit(registry, self.prefs)
        with patch('sys.stdout', new_callable=StringIO) as out:
            for seq, archive in enumerate(cli.cache._for_adf('archives')):
                if archive.title == 'My 2013 vacation':
                    cli.onecmd('upload {}'.format(seq+1))
            self.assertThat(out.getvalue(), Contains('no local copy exists'))

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

    @patch('sys.stdin', new_callable=StringIO)
    def test_do_archive(self, mock_stdin):
        cli = self._makeit(Mock(), Mock, self.prefs)
        cli.onecmd('archive')
