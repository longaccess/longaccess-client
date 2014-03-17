import os

from . import makeprefs, _temp_home
from testtools import TestCase
from mock import Mock, patch
from StringIO import StringIO
from urlparse import urlparse


class DumperTest(TestCase):
    def setUp(self):
        super(DumperTest, self).setUp()
        self.prefs = makeprefs()
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(DumperTest, self).tearDown()

    @patch('sys.stdout', new_callable=StringIO)
    def test_dummy_dumper(self, out):
        fno = {'fileno.return_value': 0,
               'read.side_effect': ["file contents man", None]}
        mrsp = Mock(**fno)
        from lacli.dumper.urls import DummyDumper
        with patch('lacli.archive.urls.urlopen', Mock(return_value=mrsp)):
            dest = DummyDumper(title='foo')
            cb = Mock()
            list(dest.dump(['http://foobar'], cb))
            self.assertTrue('dummy writing' in out.getvalue())

    def test_dumper_no_archive(self):
        from lacli.dumper import Dumper

        class MyDumper(Dumper):
            def write(self, data):
                pass
        dump = MyDumper().dump([], None)
        self.assertRaises(NotImplementedError, list, dump)

    def test_dumper_file(self):
        from lacli.dumper.file import FileDumper
        from lacli.archive.folders import FolderArchiver

        class MyDumper(FileDumper, FolderArchiver):
            pass
        with _temp_home() as tmpdir:
            dest = MyDumper(tmpdir=tmpdir)
            list(dest.dump([os.path.abspath(self.home)], lambda x, y: None))
            self.assertTrue('links' in dest.docs)
            parsed = urlparse(dest.docs['links'].local)
            self.assertTrue(not parsed.scheme or parsed.scheme == 'file')
            self.assertTrue(os.path.exists(parsed.path))
