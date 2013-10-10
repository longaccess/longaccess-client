import os
import re

from urlparse import urlunparse
from glob import iglob
from itertools import imap
from lacli.adf import (load_archive, load_all, Certificate, Archive,
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

    def prepare(self, title, folder, fmt='zip', cb=lambda x: x):
        archive = Archive(title, Meta(fmt, Cipher('aes-256-ctr', 1)))
        cert = Certificate()
        name = "{}-{}".format(date.today().isoformat(),
                              Cache._slugify(archive.title))
        files = (os.path.join(root, f)
                 for root, _, fs in os.walk(folder)
                 for f in fs)
        cipher = get_cipher(archive, cert, archive.meta.cipher)
        path, writer = self._writer(name, files, cipher)
        map(cb, writer)
        link = Links(local=urlunparse(('file', path, '', '', '', '')))
        with self._archive_open(name + ".adf", 'w') as f:
            make_adf([archive, cert, link], out=f)

    def _writer(self, name, files, cipher):
        path = os.path.join(self._cache_dir('data', write=True), name+".zip")

        def _enc(zf):
            print "Encrypting.."
            tmpargs = {'delete': False,
                       'dir': self._cache_dir('tmp', write=True)}
            with NamedTemporaryFile(suffix=".crypt", **tmpargs) as dst:
                copyfileobj(zf, CryptIO(dst, cipher))
                os.rename(dst.name, path)
        return (path, self._zip(name, files, _enc))

    def _zip(self, name, files, enc=None):
        tmpargs = {'prefix': name,
                   'dir': self._cache_dir('tmp', write=True)}
        # do it in two passes now as zip can't easily handle streaming
        with NamedTemporaryFile(**tmpargs) as zf:
            for f in zip_writer(zf, files, self):
                yield f
            # do it in two passes now as zip can't easily handle streaming
            if enc:
                enc(zf)

    def certs(self):
        return dict(imap(self._get_cert,
                         iglob(os.path.join(self._cache_dir('certs'),
                               '*.adf'))))

    def _get_cert(self, f):
        with open(f) as fh:
            return self._title_cert(load_all(fh))

    def _title_cert(self, ds):
        cs = []
        t = None
        for d in ds:
            if hasattr(d, 'key'):
                cs.append(d.key)
            if hasattr(d, 'keys'):
                cs.extend(d.keys)
            if hasattr(d, 'title'):
                t = d.title
        if t:
            return (t, cs)
