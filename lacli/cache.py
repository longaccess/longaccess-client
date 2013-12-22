import os
import shlex
from urlparse import urlparse
from pkg_resources import resource_string
from lacli.date import parse_timestamp, later

from glob import iglob
from lacli.adf import (load_archive, make_adf, Certificate, Archive,
                       Meta, Links, Cipher, Signature, as_json)
from lacli.log import getLogger
from lacli.archive import dump_archive, archive_handle
from lacli.exceptions import InvalidArchiveError
from lacli.decorators import contains
from lacli.server.interface.ClientInterface.ttypes import ArchiveStatus
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

    def get_adf(self, fname, category='archives'):
        with open(os.path.join(self._cache_dir(category), fname)) as f:
            return load_archive(f)

    @contains(dict)
    def _for_adf(self, category):
        for fn in iglob(os.path.join(self._cache_dir(category), '*.adf')):
            with open(fn) as f:
                try:
                    yield (os.path.basename(fn), load_archive(f))
                except InvalidArchiveError:
                    getLogger().debug(fn, exc_info=True)

    def prepare(self, title, items, description=None, fmt='zip', cb=None):
        docs = {
            'archive': Archive(title, Meta(fmt, Cipher('aes-256-ctr', 1)),
                               description=description),
            'cert': Certificate(),
        }
        tmpdir = self._cache_dir('data', write=True)
        if isinstance(items, basestring):
            items = [items]

        def mycb(path, rel):
            if cb is not None:
                cb(path, rel)
            elif not path:
                print "Encrypting.."
            else:
                print path.encode('utf8')
        name, path, docs['auth'] = dump_archive(
            docs['archive'], items, docs['cert'], mycb, tmpdir)
        rel = os.path.relpath(path, self.home)
        docs['links'] = Links(local=pathname2url(rel))
        docs['archive'].meta.size = os.path.getsize(path)
        tmpargs = {'delete': False,
                   'dir': self._cache_dir('archives', write=True)}
        with NamedTemporaryFile(prefix=name, suffix=".adf", **tmpargs) as f:
            make_adf(list(docs.itervalues()), out=f)
            return (f.name, docs)

    def archive_status(self, docs):
        if 'signature' in docs:
            return ArchiveStatus.Completed
        elif 'links' in docs and docs['links'].upload:
            return ArchiveStatus.InProgress
        else:
            return ArchiveStatus.Local  # TODO: check for errors

    def save_upload(self, fname, docs, uri, account):
        docs['links'].upload = uri 
        docs['archive'].meta.email = account['email']
        docs['archive'].meta.name = account['displayname']
        with self._archive_open(fname, 'w') as f:
            make_adf(list(docs.itervalues()), out=f)
        return {
            'fname': fname,
            'link': docs['links'].upload,
            'archive': docs['archive']
        }

    def upload_error(self, fname):
        docs = []
        with self._archive_open(fname) as _upload:
            docs = load_archive(_upload)
        docs['links'].upload = None
        with self._archive_open(fname, 'w') as _upload:
            make_adf(list(docs.itervalues()), out=_upload)
        return docs

    def upload_complete(self, fname, status):
        """
        adds the archive key to the signature part of the ADF file
        """
        assert 'archive_key' in status, "no archive key"
        docs = []
        with self._archive_open(fname) as _upload:
            docs = load_archive(_upload)
        docs['signature'] = Signature(aid=status['archive_key'],
                                      uri=status.get('archive'),
                                      expires=status.get('expires'),
                                      created=status.get('created'),
                                      creator=docs['archive'].meta.name)
        with self._archive_open(fname, 'w') as _upload:
            make_adf(list(docs.itervalues()), out=_upload)
        return docs

    def save_cert(self, docs):
        """
        write cert documents to the cache directory under a unique filename.
        """
        fname = archive_handle(list(docs.itervalues()))
        tmpargs = {'delete': False,
                   'dir': self._cache_dir('certs', write=True),
                   'suffix': ".adf",
                   'prefix': fname}
        certs = self.certs()
        aid = docs['signature'].aid  # let's check if we already have this cert
        uri = docs['signature'].uri
        if not aid in certs or uri != certs[aid]['signature'].uri:
            with NamedTemporaryFile(**tmpargs) as f:
                make_adf(list(docs.itervalues()), out=f)
                return (aid, f.name)
        else:
            return (aid, None)

    def import_cert(self, fname):
        with open(fname) as cert:
            docs = load_archive(cert)
            return self.save_cert(docs)

    def _printable_cert(self, docs):
        archive = docs['archive']
        cipher = archive.meta.cipher
        if hasattr(cipher, 'mode'):
            cipher = cipher.mode
        created = parse_timestamp(archive.meta.created)
        expires = None
        aid = "-"
        if 'signature' in docs:
            aid = docs['signature'].aid or aid
            if docs['signature'].expires is not None:
		expires = parse_timestamp(docs['signature'].expires)
            if docs['signature'].created is not None:
                created = parse_timestamp(docs['signature'].created)
        md5 = b2a_hex(docs['auth'].md5).upper()
        key = b2a_hex(docs['cert'].key).upper()
        hk = pairs(fours(pairs(iter(key))), " . ")

        return unicode(resource_string(__name__, "data/certificate.html")).format(
            json=as_json(docs),
            aid=aid,
            keyB=next(hk),
            keyC=next(hk),
            keyD=next(hk),
            keyE=next(hk),
            name=archive.meta.name or "",
            email=archive.meta.email or "",
            uploaded=created.strftime("%c"),
            expires=(expires and expires.strftime("%c")) or "unknown",
            title=archive.title or "",
	    size=archive.meta.size,
            desc=archive.description or "",
	    md5=" . ".join(fours(pairs(iter(md5)))),
	    fmt=archive.meta.format,
            cipher=cipher).encode('utf8')

    def shred_file(self, fname, srm=None):
        commands = []
        if srm:
            commands.append(srm)
        else:
            commands.append('srm')
            commands.append('shred')
            commands.append('gshred')
            commands.append('sdelete')
            commands.append(
                'Eraser.exe addtask --schedule=now -q --file={file}')
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

    def shred_archive(self, fname, srm=None):
        fname = os.path.join(self._cache_dir('archives'), fname)
        self.shred_file(fname, srm)
        return fname

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

    def export_cert(self, aid):
        for fname, docs in self._for_adf('certs').iteritems():
            if 'signature' in docs and aid == docs['signature'].aid:
                text = 'longaccess-{}.yaml'.format(aid)
                with open(text, 'w') as f:
                    make_adf(list(docs.itervalues()), out=f, pretty=True)
                return text

    def print_cert(self, aid):
        for fname, docs in self._for_adf('certs').iteritems():
            if 'signature' in docs and aid == docs['signature'].aid:
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


if __name__ == "__main__":
    import hashlib
    cache = Cache(os.path.expanduser(os.path.join("~", ".longaccess")))
    for fname, docs in cache._for_adf('archives').iteritems():
        path = os.path.join(cache.home, docs['links'].local)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            md5 = hashlib.md5()
            while 1:
                buf = f.read(16*1024)
                if not buf:
                    break
                md5.update(buf)
            assert md5.digest() == docs['auth'].md5, path
