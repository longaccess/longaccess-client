import os
import sys
import hashlib

from tempfile import NamedTemporaryFile
from lacli.adf import Auth, make_adf
from lacli.crypt import CryptIO
from lacli.cipher import get_cipher
from lacli.hash import HashIO
from lacli.enc import get_unicode
from shutil import copyfileobj
from zipfile import ZipFile, ZIP_DEFLATED
from itertools import imap
from contextlib import contextmanager
try:
    import zipstream
except ImportError:
    zipstream = None


def archive_handle(docs):
    h = HashIO()
    make_adf(docs, out=h)
    return h.getvalue().encode('hex')


def restore_archive(archive, path, cert, folder, tmpdir, cb=None):
    cipher = get_cipher(archive, cert)
    with open(path, 'rb') as infile:
        with NamedTemporaryFile() as dst:
            with CryptIO(infile, cipher) as cf:
                copyfileobj(cf, dst)
            dst.flush()
            dst.seek(0)
            with ZipFile(dst) as zf:
                map(cb,
                    map(lambda zi: zf.extract(zi, folder), zf.infolist()))


class MyHashObj(object):
    hashf = None

    def __init__(self, hashf='sha512'):
        self.md5 = hashlib.md5()
        if hasattr(hashlib, hashf):
            self.hashf = hashf
            setattr(self, hashf, getattr(hashlib, hashf)())

    def update(self, data):
        self.md5.update(data)
        if self.hashf:
            getattr(self, self.hashf).update(data)

    def auth(self):
        args = {'md5': self.md5.digest()}
        if self.hashf:
            args[self.hashf] = getattr(self, self.hashf).digest()
        return Auth(**args)


def dump_archive(archive, items, cert, cb=None, tmpdir='/tmp',
                 hashf='sha512'):
    name = archive_handle([archive, cert])
    cipher = get_cipher(archive, cert)
    hashobj = MyHashObj(hashf)

    if sys.platform.startswith('win'):
        # windows has unicode file system api
        items = map(unicode, items)

    path = _writer(name, items, cb,
                   cipher, tmpdir, hashobj)

    return (name, path, hashobj.auth())


@contextmanager
def _temp_file(fdst, name, tmpdir):
    with NamedTemporaryFile(prefix=name, dir=tmpdir) as zf:
        yield zf
        zf.flush()
        zf.seek(0)
        with fdst as dst:
            copyfileobj(zf, dst, 1024)


def walk_folders(folders):
    for folder in folders:
        if not os.path.isdir(folder):
            yield (folder, os.path.basename(folder))
        else:
            for root, _, fs in os.walk(folder):
                for f in fs:
                    path = os.path.join(root, f)
                    strip = os.path.dirname(folder)
                    rel = os.path.relpath(path, strip)
                    yield (path, get_unicode(rel))


def _writer(name, items, cb, cipher, tmpdir, hashobj=None):

    tmpargs = {'delete': False,
               'suffix': ".longaccess",
               'dir': tmpdir,
               'prefix': name}
    dst = NamedTemporaryFile(**tmpargs)

    fdst = CryptIO(dst, cipher, hashobj=hashobj)

    if zipstream is None:
        # do it in two passes now as vanilla zipfile
        # can't easily handle streaming
        fdst = _temp_file(fdst, name, tmpdir)

    files = walk_folders(imap(os.path.abspath, items))

    def _args():
        for path, rel in files:
            try:
                cb(path, rel)
                yield ((path,), {'arcname': rel.encode('utf-8')})
            except Exception as e:
                if not hasattr(e, 'filename'):
                    setattr(e, 'filename', path)
                raise

    try:
        with fdst as zf:
            zipargs = {'mode': 'w', 'compression': ZIP_DEFLATED,
                       'allowZip64': True}
            if zipstream is None:
                with ZipFile(zf, **zipargs) as zpf:
                    for args, kwargs in _args():
                        zpf.write(*args, **kwargs)
            else:
                with zipstream.ZipFile(**zipargs) as zpf:
                    zpf.paths_to_write = _args()
                    for chunk in zpf:
                        zf.write(chunk)
    except Exception:
        path = dst.name
        dst.close()
        if os.path.exists(path):
            os.unlink(path)  # don't leave trash
        raise
    return dst.name
