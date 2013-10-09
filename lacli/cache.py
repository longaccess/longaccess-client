import os
import re

from urlparse import urlunparse
from glob import iglob
from itertools import imap
from lacli.adf import (load_archive, Certificate, Archive,
                       Meta, Links, make_adf, Cipher)
from lacli.log import getLogger
from unidecode import unidecode
from datetime import date
from lacli.zip import zip_writer
from tempfile import NamedTemporaryFile
from lacli.crypt import CryptIO
from lacli.cipher import get_cipher
from shutil import copyfileobj


class Cache(object):
    def __init__(self, home):
        self.home = home

    def _cache_dir(self, path, write=False):
        dname = os.path.join(self.home, path)
        if not os.path.exists(dname) and write:
            os.makedirs(dname, mode=0744)
        return dname

    def _archive_open(self, name, mode='r'):
        dname = self._cache_dir('archives', write='w' in mode)
        return open(os.path.join(dname, name), mode)

    def archives(self):
        def getit(fn):
            with open(fn) as f:
                a = load_archive(f)
                if a:
                    return a
            getLogger().debug(
                "ADF file '{}' didn't contain archive description!".format(fn))
        fs = iglob(os.path.join(self._cache_dir('archives'), '*.adf'))
        return filter(None, imap(getit, fs))

    _slugify_strip_re = re.compile(r'[^\w\s-]')
    _slugify_hyphenate_re = re.compile(r'[-\s]+')

    @classmethod
    def _slugify(cls, value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        From Django's "django/template/defaultfilters.py".
        """
        if not isinstance(value, unicode):
            value = unicode(value)
        return unicode(cls._slugify_hyphenate_re.sub(
            '-', cls._slugify_strip_re.sub('', unidecode(value))
            ).strip().lower())

    def prepare(self, title, folder, fmt='zip'):
        cipher = Cipher('aes-256-ctr', 1)
        archive = Archive(title, Meta(fmt, cipher))
        for f in self._dump(archive, folder):
            print "Added ", f

    def _dump(self, archive, folder):
        name = "{}-{}".format(
            date.today().isoformat(),
            Cache._slugify(archive.title))
        link = Links(local=urlunparse(
            ('file', os.path.join(self._cache_dir('data'), name + ".zip"),
             '', '', '', '')))
        cert = Certificate()
        cipher = get_cipher(archive, cert, archive.meta.cipher)
        with self._archive_open(name + ".adf", 'w') as f:
            make_adf([archive, cert, link], out=f)
            files = (os.path.join(root, f)
                     for root, _, fs in os.walk(folder)
                     for f in fs)
            return self._writer(name, files, cipher)

    def _writer(self, name, files, cipher):
        tmpdir = self._cache_dir('tmp', write=True)
        datadir = self._cache_dir('data', write=True)
        # do it in two passes now as zip can't easily handle streaming
        kwargs = {'prefix': name, 'dir': tmpdir, 'delete': True}
        with NamedTemporaryFile(suffix=".zip", **kwargs) as zf:
            for f in zip_writer(zf, files, self):
                yield f
            print "Encrypting.."
            kwargs['delete'] = False
            with NamedTemporaryFile(suffix=".crypt", **kwargs) as dst:
                copyfileobj(zf, CryptIO(dst, cipher))
                os.rename(dst.name, os.path.join(datadir, name))
