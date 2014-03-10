import os
import sys

from tempfile import NamedTemporaryFile
from lacli.adf import make_adf
from lacli.crypt import CryptIO
from lacli.cipher import get_cipher
from lacli.hash import HashIO
from lacli.enc import get_unicode
from lacli.auth import MyHashObj
from .zip import writer as zip_writer
from shutil import copyfileobj
from zipfile import ZipFile
from itertools import imap


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


def dump_archive(archive, items, cert, cb=None, tmpdir='/tmp',
                 hashf='sha512'):
    name = archive_handle([archive, cert])
    cipher = get_cipher(archive, cert)
    hashobj = MyHashObj(hashf)

    if sys.platform.startswith('win'):
        # windows has unicode file system api
        items = map(unicode, items)

    path = zip_writer(name, _zip_paths(items, cb),
                      cipher, tmpdir, hashobj)

    return (name, path, hashobj.auth())


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


def _zip_paths(items, cb):
    for path, rel in walk_folders(imap(os.path.abspath, items)):
        try:
            cb(path, rel)
            yield ((path,), {'arcname': rel.encode('utf-8')})
        except Exception as e:
            if not hasattr(e, 'filename'):
                setattr(e, 'filename', path)
            raise
