import os

from . import makeprefs, dummyarchive
from testtools import TestCase
from testtools.matchers import Contains
from mock import Mock, patch
from StringIO import StringIO


class FetchCommandTest(TestCase):
    def setUp(self):
        super(FetchCommandTest, self).setUp()
        self.prefs = makeprefs()
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(FetchCommandTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.command import LaFetchCommand
        return LaFetchCommand(*args, **kwargs)

    def _makeupload(self, *args, **kwargs):
        return Mock(upload=Mock(**kwargs))

    def test_command(self):
        assert self._makeit(Mock(), Mock(), self.prefs)

    def test_fetch_archive_nonexistent(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            registry = Mock()
            registry.prefs = self.prefs
            registry.session.archives.return_value = ()
            cli = self._makeit(registry)
            cli.onecmd('fetch baz')
            self.assertEqual("Archive not found\n", out.getvalue())

    def test_fetch_archive(self):
        with patch('sys.stdout', new_callable=StringIO) as out:
            with patch('lacli.command.ask_key') as ask_key:
                ask_key.return_value = 'DEADBEEF' * 8
                registry = Mock()
                registry.prefs = self.prefs
                registry.cache.save_cert.return_value = ('LALA', None)

                registry.session.archives.return_value = (dummyarchive,)
                cli = self._makeit(registry)
                cli.onecmd('fetch baz')
                self.assertThat(out.getvalue(),
                                Contains('Fetched certificate LALA'))

                docs = registry.cache.save_cert.call_args[0][0]
                self.assertTrue('cert' in docs)
                self.assertTrue('archive' in docs)
                self.assertTrue('signature' in docs)
                self.assertEqual(docs['archive'].title, 'faz')
