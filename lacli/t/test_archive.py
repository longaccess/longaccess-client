# -*- coding: utf-8 -*-
import os

from testtools import TestCase
from . import makeprefs, dummykey
from shutil import rmtree, copy
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

    def test_slugify(self):
        from lacli.archive import _slugify
        self.assertEqual(_slugify("This is a test"), "this-is-a-test")
        self.assertEqual(_slugify(u"γειά σου ρε"), "geia-sou-re")

    def test_restore(self):
        from lacli.archive import restore_archive
        from lacli.adf import Archive, Meta, Cipher
        from lacli.crypt import CryptIO
        from lacli.cipher import get_cipher
        from zipfile import ZipFile
        from shutil import copyfileobj
        with self._temp_home() as home:
            cdir = os.path.join(home, 'certs')
            os.makedirs(cdir)
            tmpdir = os.path.join(home, 'tmp')
            os.makedirs(tmpdir)
            adf = os.path.join(self.home, 'archives', 'sample.adf')
            copy(adf, cdir)
            cert = Mock(key=dummykey)
            archive = Archive('My 2013 vacation',
                              Meta('zip', Cipher('aes-256-ctr', 1)))
            zf = os.path.join(tmpdir, 'test.zip')
            with ZipFile(zf, 'w') as zpf:
                zpf.write(adf)
            cf = os.path.join(tmpdir, 'test.zip.crypt')
            with open(zf):
                with open(cf, 'w') as dst:
                    copyfileobj(open(zf),
                                CryptIO(dst, get_cipher(archive, cert)))
            restore_archive(archive, cf, cert, tmpdir, tmpdir)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, adf)))
