import os

from glob import iglob
from lacli.adf import (load_archive, make_adf, Certificate, Archive,
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

    def _upload_open(self, name, mode='r'):
        dname = self._cache_dir('uploads', write='w' in mode)
        return open(os.path.join(dname, name), mode)

    @contains(list)
    def archives(self, full=False, category='archives'):
        for fn in iglob(os.path.join(self._cache_dir(category), '*.adf')):
            with open(fn) as f:
                try:
                    if full:
                        yield load_archive(f)
                    else:
                        yield load_archive(f)['archive']
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
        archive.meta.size = os.path.getsize(path)
        with self._archive_open(name + ".adf", 'w') as f:
            make_adf([archive, cert, auth, link], out=f)

    def save_upload(self, docs, upload):
        docs['links'].upload = upload['uri']
        with self._upload_open(upload['id'] + ".adf", 'w') as f:
            make_adf(docs, out=f)

    def links(self):
        return self._by_title('links', iglob(
            os.path.join(self._cache_dir('archives'), '*.adf')))

    def certs(self):
        return self._by_title('cert', iglob(
            os.path.join(self._cache_dir('certs'), '*.adf')))

    @contains(dict)
    def _by_title(self, key, fs):
        for f in fs:
            with open(f) as fh:
                try:
                    docs = load_archive(fh)
                    if key in docs:
                        yield (docs['archive'].title, docs[key])
                except InvalidArchiveError:
                    getLogger().debug(f, exc_info=True)
