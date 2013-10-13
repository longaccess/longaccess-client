import os

from glob import iglob
from lacli.adf import (load_archive, make_adf, load_all, Certificate, Archive,
                       Meta, Links, Cipher)
from lacli.log import getLogger
from lacli.archive import dump_archive
from lacli.exceptions import InvalidArchiveError
from lacli.decorators import contains
from urlparse import urlunparse


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

    def _cert_open(self, name, mode='r'):
        dname = self._cache_dir('certs', write='w' in mode)
        return open(os.path.join(dname, name), mode)

    @contains(list)
    def archives(self):
        for fn in iglob(os.path.join(self._cache_dir('archives'), '*.adf')):
            with open(fn) as f:
                try:
                    yield load_archive(f)
                except InvalidArchiveError:
                    getLogger().debug(fn, exc_info=True)

    def prepare(self, title, folder, fmt='zip', cb=None):
        archive = Archive(title, Meta(fmt, Cipher('aes-256-ctr', 1)))
        cert = Certificate()
        tmpdir = self._cache_dir('tmp', write=True)
        name, tmppath, auth = dump_archive(archive, folder, cert, cb, tmpdir)
        path = os.path.join(self._cache_dir('data', write=True), name)
        os.rename(tmppath, path)
        link = Links(local=urlunparse(('file', path, '', '', '', '')))
        with self._archive_open(name + ".adf", 'w') as f:
            make_adf([archive, link], out=f)
        with self._cert_open(name + ".adf", 'w') as f:
            make_adf([archive, cert, auth], out=f)

    def links(self):
        return self._by_title(
            lambda d: hasattr(d, 'local') or hasattr(d, 'download'),
            iglob(os.path.join(self._cache_dir('archives'), '*.adf')))

    def certs(self):
        return self._by_title(
            lambda d: hasattr(d, 'key') or hasattr(d, 'keys'),
            iglob(os.path.join(self._cache_dir('certs'), '*.adf')))

    @contains(dict)
    def _by_title(self, predicate, fs):
        for f in fs:
            with open(f) as fh:
                docs = load_all(fh)
                value = None
                title = None
                for d in docs:
                    if predicate(d):
                        value = d
                    if hasattr(d, 'title'):
                        title = d.title
                if title:
                    yield (title, value)
