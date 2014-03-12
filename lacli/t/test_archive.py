# -*- coding: utf-8 -*-
import os
import sys
import operator
import zipfile

from StringIO import StringIO
from testtools import TestCase
from unittest import SkipTest
from . import makeprefs
from shutil import rmtree
from contextlib import contextmanager
from tempfile import mkdtemp, NamedTemporaryFile
from mock import MagicMock, Mock, patch


class ArchiveTest(TestCase):
    def setUp(self):
        super(ArchiveTest, self).setUp()
        self.prefs = makeprefs()
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(ArchiveTest, self).tearDown()

    @contextmanager
    def _temp_home(self):
        d = mkdtemp()
        yield d
        rmtree(d)

    def test_restore(self):
        from lacli.archive import restore_archive
        from lacli.cache import Cache
        cache = Cache(self.home)
        cert = cache.certs()['74-5N93']
        with self._temp_home() as tmpdir:
            cb = Mock()
            cfname = os.path.join(
                self.home, 'data', '2013-10-22-foobar.zip.crypt')
            restore_archive(
                cert['archive'], cfname, cert['cert'], tmpdir, tmpdir, cb)
            self.assertEqual(1, cb.call_count)
            self.assertTrue(os.path.exists(
                os.path.join(tmpdir, 'xtQz6ziJ.sh.part')))

    def test_walk_folders(self):
        from lacli.archive.folders import walk_folders
        sample = None
        files = [os.path.abspath(self.home),
                 os.path.abspath(
                     os.path.join('t', 'data', 'longaccess-74-5N93.html'))]
        for p, r in walk_folders(files):
            self.assertEqual(unicode, type(r))
            if r.endswith('sample.adf'):
                sample = r
        self.assertEqual("home/archives/sample.adf", sample)

    def test_folder_args(self):
        from lacli.archive.folders import FolderArchiver

        cb = Mock()
        ar = FolderArchiver()
        for a, k in ar.args([self.home], cb):
            self.assertTrue('arcname' in k)
            self.assertEqual(str, type(k['arcname']))

        self.assertTrue(u'home/archives/sample.adf' in
                        map(operator.itemgetter(1),
                            map(operator.itemgetter(0),
                                cb.call_args_list)))

    def test_folder_args_exception(self):
        from lacli.archive.folders import FolderArchiver

        cb = Mock(side_effect=Exception())
        ar = FolderArchiver()
        args = ar.args([self.home], cb)
        e = self.assertRaises(Exception, list, args)
        self.assertTrue(hasattr(e, 'filename'))

    def test_url_args(self):
        murl = Mock(return_value=StringIO("file contents"))
        from lacli.archive.urls import UrlArchiver
        with patch('lacli.archive.urls.urlopen', murl):
            cb = Mock()
            ar = UrlArchiver()
            a, k = next(ar.args(['http://foobar'], cb))
            self.assertTrue('arcname' in k)
            self.assertEqual(str, type(k['arcname']))
            self.assertEqual('foobar', k['arcname'])
            self.assertEqual('foobar', cb.call_args[0][1])
            with a[0] as contents:
                self.assertEqual('file contents', contents.read())

    def test_zip_archiver_tempfile(self):
        from lacli.archive.zip import ZipArchiver
        ar = ZipArchiver()
        foo = MagicMock()
        with ar._temp_file(foo) as f:
            f.write("BAR")
        foo.__enter__.assert_called()
        foo.__enter__.return_value.write.assert_called_with("BAR")

    def test_zip_archiver_args(self):
        from lacli.archive.zip import ZipArchiver
        ar = ZipArchiver()
        cb = Mock()
        self.assertEqual([], list(ar.args([], cb)))
        cb.assert_not_called()
        self.assertEqual([(('bar',), {})], list(ar.args(['bar'], cb)))
        cb.assert_called_with('bar', 'bar')

    def test_zip_archiver_no_zipstream(self):
        orig_import = __import__

        def import_mock(name, *args):
            if name == 'zipstream':
                raise ImportError()
            return orig_import(name, *args)
        with patch('__builtin__.__import__', side_effect=import_mock):
            if 'lacli.archive.zip' in sys.modules:
                del sys.modules['lacli.archive.zip']
            import lacli.archive.zip as azip
            with NamedTemporaryFile() as f:
                dst = MagicMock()
                dst.__enter__.return_value = f
                ar = azip.ZipArchiver()
                ar._temp_file = Mock(return_value=dst)
                list(ar.archive([os.path.abspath(os.path.join(
                    't', 'data', 'longaccess-74-5N93.html'))], dst, None))
                dst.__enter__.assert_called()
                ar._temp_file.assert_called()
                z = zipfile.ZipFile(f)
                z.testzip()

    def test_zip_archiver_zipstream(self):
        try:
            import zipstream  # noqa
        except ImportError:
            raise SkipTest("requires python-zipstream")
        if 'lacli.archive.zip' in sys.modules:
            del sys.modules['lacli.archive.zip']
        from lacli.archive.zip import ZipArchiver

        with NamedTemporaryFile() as f:
            dst = MagicMock()
            dst.__enter__.return_value = f
            ar = ZipArchiver()
            ar._temp_file = Mock(return_value=dst)
            list(ar.archive([os.path.abspath(os.path.join(
                't', 'data', 'longaccess-74-5N93.html'))], dst, None))
            dst.__enter__.assert_called()
            ar._temp_file.assert_not_called()
            z = zipfile.ZipFile(f)
            z.testzip()

    def test_archive_handle(self):
        from lacli.archive import archive_handle
        self.assertEqual('ff612b0d511eaf22c4b50c2ba1e98260',
                         archive_handle(['foo', 'bar']))
