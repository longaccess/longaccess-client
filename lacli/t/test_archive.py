# -*- coding: utf-8 -*-
import os
import operator

from StringIO import StringIO
from testtools import TestCase
from . import makeprefs
from shutil import rmtree
from contextlib import contextmanager
from tempfile import mkdtemp
from mock import Mock, patch
from lacli.adf import Archive, Meta, Certificate
from zipfile import ZipFile


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
        from lacli.archive import walk_folders
        sample = None
        for p, r in walk_folders([os.path.abspath(self.home)]):
            self.assertEqual(unicode, type(r))
            if r.endswith('sample.adf'):
                sample = r
        self.assertEqual("home/archives/sample.adf", sample)

    def test_zip_paths(self):
        from lacli.archive import _zip_paths

        cb = Mock()
        for a, k in _zip_paths([self.home], cb):
            self.assertTrue('arcname' in k)
            self.assertEqual(str, type(k['arcname']))

        self.assertTrue(u'home/archives/sample.adf' in
                        map(operator.itemgetter(1),
                            map(operator.itemgetter(0),
                                cb.call_args_list)))

    def test_zip_urls(self):
        murl = Mock(return_value=StringIO("file contents"))
        with patch('urllib2.urlopen', murl):
            from lacli.archive.urls import args
            cb = Mock()
            a, k = next(args(['http://foobar'], cb))
            self.assertTrue('arcname' in k)
            self.assertEqual(str, type(k['arcname']))
            self.assertEqual('foobar', k['arcname'])
            self.assertEqual('foobar', cb.call_args[0][1])

    def test_dump_urls(self):
        fno = {'fileno.return_value': 0,
               'read.side_effect': ["file contents man", None]}
        mrsp = Mock(**fno)
        with patch('urllib2.urlopen', Mock(return_value=mrsp)):
            with self._temp_home() as tmpdir:
                from lacli.archive.urls import dump_urls
                cb = Mock()
                archive = Archive('foo', Meta(
                    format='zip', cipher='xor', created='now'))
                name, path, auth = dump_urls(
                    archive, ['http://foobar'], Certificate('\0'*8),
                    cb, tmpdir=tmpdir)
                self.assertTrue(os.path.exists(path))
                with ZipFile(path) as zf:
                    for zi in zf.infolist():
                        zf.extract(zi, tmpdir)
                path = os.path.join(tmpdir, "foobar")
                self.assertTrue(os.path.exists(path))
                with open(path) as f:
                    self.assertEqual("file contents man", f.read())
