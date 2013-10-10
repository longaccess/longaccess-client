import os

from glob import iglob
from itertools import imap
from lacli.adf import (load_archive, make_adf, load_all, Certificate, Archive,
                       Meta, Links, Cipher)
from lacli.log import getLogger
from lacli.archive import dump_archive
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

    def prepare(self, title, folder, fmt='zip', cb=lambda x: x):
        archive = Archive(title, Meta(fmt, Cipher('aes-256-ctr', 1)))
        cert = Certificate()
        tmpdir = self._cache_dir('tmp', write=True)
        name, tmppath = dump_archive(archive, folder, cert, cb, tmpdir)
        path = os.path.join(self._cache_dir('data', write=True), name)
        os.rename(tmppath, path)
        link = Links(local=urlunparse(('file', path, '', '', '', '')))
        with self._archive_open(name + ".adf", 'w') as f:
            make_adf([archive, link], out=f)
        with self._cert_open(name + ".adf", 'w') as f:
            make_adf([archive, cert], out=f)

    def links(self):
        return dict(imap(self._get_link,
                         iglob(os.path.join(self._cache_dir('archives'),
                               '*.adf'))))

    def certs(self):
        return dict(imap(self._get_cert,
                         iglob(os.path.join(self._cache_dir('certs'),
                               '*.adf'))))

    def _get_link(self, f):
        with open(f) as fh:
            docs = load_all(fh)
            link = None
            t = None
            for d in docs:
                if hasattr(d, 'local') or hasattr(d, 'download'):
                    link = d
                if hasattr(d, 'title'):
                    t = d.title
            if t:
                return (t, link)

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
