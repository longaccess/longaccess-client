import os

from glob import iglob
from lacli.adf import (load_archive, make_adf, Certificate, Archive,
                       Meta, Links, Cipher)
from lacli.log import getLogger
from lacli.archive import dump_archive, archive_slug
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

    @contains(dict)
    def _for_adf(self, category):
        for fn in iglob(os.path.join(self._cache_dir(category), '*.adf')):
            with open(fn) as f:
                try:
                    yield (fn, load_archive(f))
                except InvalidArchiveError:
                    getLogger().debug(fn, exc_info=True)

    @contains(list)
    def archives(self, full=False, category='archives'):
        for docs in self._for_adf(category).itervalues():
            if full:
                yield docs
            else:
                yield docs['archive']

    @contains(list)
    def uploads(self):
        for fname, docs in self._for_adf('uploads').iteritems():
            if 'links' in docs and hasattr(docs['links'], 'upload'):
                yield {
                    'fname': fname,
                    'link': docs['links'].upload,
                    'archive': docs['archive']
                }

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
        with self._upload_open("{}.adf".format(upload['id']), 'w') as f:
            make_adf(list(docs.itervalues()), out=f)

    def save_cert(self, upload, status):
        assert 'archive_uri' in status, "no archive uri"
        with open(upload['fname']) as _upload:
            docs = load_archive(_upload)
            docs['links'] = Links(download=status['archive_uri'])
            fname = archive_slug(docs['archive'])
            with self._cert_open(fname, 'w') as f:
                make_adf(list(docs.itervalues()), out=f)
        getLogger().debug(
            "removing {}".format(upload['fname']))
        os.unlink(upload['fname'])

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
