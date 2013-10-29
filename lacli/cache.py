import os
import shlex
from urlparse import urlparse
from pkg_resources import resource_string
from dateutil.parser import parse as date_parse
from dateutil.relativedelta import relativedelta as date_delta

from glob import iglob
from lacli.adf import (load_archive, make_adf, Certificate, Archive,
                       Meta, Links, Cipher, Signature, as_json)
from lacli.log import getLogger
from lacli.archive import dump_archive, archive_slug
from lacli.exceptions import InvalidArchiveError
from lacli.decorators import contains
from urllib import pathname2url
from tempfile import NamedTemporaryFile
from binascii import b2a_hex
from itertools import izip, imap
from subprocess import check_call


def group(it, n, dl):
    return imap(dl.join, izip(*[it]*n))


def pairs(it, dl=""):
    return group(it, 2, dl)


def fours(it, dl=" "):
    return group(it, 4, dl)


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

    def prepare(self, title, folder, fmt='zip', cb=None):
        archive = Archive(title, Meta(fmt, Cipher('aes-256-ctr', 1)))
        cert = Certificate()
        tmpdir = self._cache_dir('data', write=True)
        name, path, auth = dump_archive(archive, folder, cert, cb, tmpdir)
        link = Links(local=pathname2url(os.path.relpath(path, self.home)))
        archive.meta.size = os.path.getsize(path)
        tmpargs = {'delete': False,
                   'dir': self._cache_dir('archives', write=True)}
        with NamedTemporaryFile(prefix=name, suffix=".adf", **tmpargs) as f:
            make_adf([archive, cert, auth, link], out=f)

    def save_upload(self, fname, docs, upload):
        docs['links'].upload = upload['uri']
        docs['archive'].meta.email = upload['account']['email']
        docs['archive'].meta.name = upload['account']['displayname']
        with open(fname, 'w') as f:
            make_adf(list(docs.itervalues()), out=f)
        return {
            'fname': fname,
            'link': docs['links'].upload,
            'archive': docs['archive']
        }

    def upload_complete(self, fname, status):
        """
        adds the archive key to the signature part of the ADF file
        """
        assert 'archive_key' in status, "no archive key"
        docs = []
        with open(fname) as _upload:
            docs = load_archive(_upload)
        docs['signature'] = Signature(aid=status['archive_key'],
                                      uri='http://longaccess.com/a/')
        with open(fname, 'w') as _upload:
            make_adf(list(docs.itervalues()), out=_upload)
        return docs

    def save_cert(self, docs):
        """
        write cert documents to the cache directory under a unique filename.
        """
        fname = archive_slug(docs['archive'])
        tmpargs = {'delete': False,
                   'dir': self._cache_dir('certs', write=True)}
        with NamedTemporaryFile(prefix=fname, suffix=".adf", **tmpargs) as f:
            make_adf(list(docs.itervalues()), out=f)
        return docs['signature'].aid

    def import_cert(self, fname):
        with open(fname) as cert:
            docs = load_archive(cert)
            self.save_cert(docs)
            return docs['signature'].aid

    def _printable_cert(self, docs):
        archive = docs['archive']
        cipher = archive.meta.cipher
        if hasattr(cipher, 'mode'):
            cipher = cipher.mode
        created = date_parse(archive.meta.created)
        expires = created + date_delta(years=30)
        md5 = b2a_hex(docs['auth'].md5).upper()
        key = b2a_hex(docs['cert'].key).upper()
        hk = pairs(fours(pairs(iter(key))), " . ")

        return resource_string(__name__, "data/certificate.html").format(
            json=as_json(docs),
            aid=docs['links'].download,
            keyB=next(hk),
            keyC=next(hk),
            keyD=next(hk),
            keyE=next(hk),
            name=archive.meta.name,
            email=archive.meta.email,
            uploaded=created.strftime("%c"),
            expires=expires.strftime("%c"),
            title=archive.title,
            desc=archive.description,
            md5=" . ".join(fours(pairs(iter(md5)))),
            fmt=archive.meta.format,
            cipher=cipher)

    def shred_file(self, fname, srm=None):
        commands = []
        if srm:
            commands.append(srm)
        else:
            commands.append('srm')
            commands.append('shred')
            commands.append('gshred')
            commands.append('sdelete')
            commands.append('Eraser.exe addtask --schedule=now -q --file={file}')
        for command in commands:
            try:
                newcommand = command.format(file=fname)
                args = shlex.split(newcommand)
                if command == newcommand:
                    args.append(fname)
                if 0 == check_call(args):
                    getLogger().debug("success running {}".format(command))
                    if os.path.exists(fname):
                        os.unlink(fname)
            except Exception:
                getLogger().debug("error running {}".format(command),
                                  exc_info=True)

    def shred_cert(self, aid, countdown=[], srm=None):
        path = None
        for fname, docs in self._for_adf('certs').iteritems():
            if 'links' in docs and aid == docs['links'].download:
                path = fname
            elif 'signature' in docs and aid == docs['signature'].aid:
                path = fname
        if path:
            for a in countdown:
                pass
            self.shred_file(path, srm)
            return path

    def print_cert(self, aid):
        for fname, docs in self._for_adf('certs').iteritems():
            if 'links' in docs and aid == docs['links'].download:
                html = 'longaccess-{}.html'.format(aid)
                with open(html, 'w') as f:
                    f.write(self._printable_cert(docs))
                return html

    @contains(dict)
    def certs(self, files=[]):
        if not files:
            files = iglob(os.path.join(self._cache_dir('certs'), '*.adf'))
        for f in files:
            with open(f) as fh:
                try:
                    docs = load_archive(fh)
                    if 'signature' in docs:
                        yield (docs['signature'].aid, docs)
                except InvalidArchiveError:
                    getLogger().debug(f, exc_info=True)

    def data_file(self, link):
        try:
            parsed = urlparse(link.local)
            assert not parsed.scheme or parsed.scheme == 'file'
            return os.path.join(self.home, parsed.path)
        except:
            return None
        
