# -*- coding: utf-8 -*-
import os
import operator

from testtools import TestCase
from . import makeprefs
from shutil import rmtree
from contextlib import contextmanager
from tempfile import mkdtemp
from mock import Mock


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
