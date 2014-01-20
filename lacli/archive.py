import os
import sys
import re
import hashlib

from unidecode import unidecode
from datetime import date
from tempfile import NamedTemporaryFile
from lacli.adf import Auth, make_adf
from lacli.crypt import CryptIO
from lacli.cipher import get_cipher
from lacli.hash import HashIO
from shutil import copyfileobj
from zipfile import ZipFile, ZIP_DEFLATED
from itertools import starmap


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def _slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    From Django's "django/template/defaultfilters.py".
    """
    if not isinstance(value, unicode):
        value = unicode(value)
    return unicode(_slugify_hyphenate_re.sub(
        '-', _slugify_strip_re.sub('', unidecode(value))
        ).strip().lower())


def archive_slug(archive):
    return "{}-{}".format(date.today().isoformat(),
                          _slugify(archive.title))


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

    path, writer = _writer(name, items,
                           cipher, tmpdir, hashobj)
    try:
        list(starmap(cb, writer))
    except Exception as e:
        if os.path.exists(path):
            os.unlink(path)  # don't leave trash
        raise e
    return (name, path, hashobj.auth())


def walk_folders(folders):
    fsenc = sys.getfilesystemencoding() or "UTF-8"

    def get_unicode_filename(fname):
        if isinstance(fname, unicode):
            return fname
        try:
            return fname.decode(fsenc)
        except UnicodeDecodeError:
            if fsenc == 'UTF-8':
                raise
            return fname.decode('UTF-8')

    for folder in folders:
        if not os.path.isdir(folder):
            yield (folder, os.path.basename(folder))
        else:
            for root, _, fs in os.walk(folder):
                for f in fs:
                    path = os.path.join(root, f)
                    strip = os.path.dirname(folder)
                    rel = os.path.relpath(path, strip)
                    yield (path, get_unicode_filename(rel))


def _writer(name, items, cipher, tmpdir, hashobj=None):
    tmpargs = {'delete': False,
               'suffix': ".longaccess",
               'dir': tmpdir,
               'prefix': name}
    dst = NamedTemporaryFile(**tmpargs)

    def _enc():
        # do it in two passes now as zip can't easily handle streaming
        tmpargs = {'prefix': name,
                   'dir': tmpdir}
        with NamedTemporaryFile(**tmpargs) as zf:
            with ZipFile(zf, 'w', ZIP_DEFLATED, True) as zpf:
                for path, rel in walk_folders(map(os.path.abspath, items)):
                    try:
                        zpf.write(path, unicode(rel).encode('utf-8'))
                    except Exception as e:
                        if not hasattr(e, 'filename'):
                            setattr(e, 'filename', path)
                        dst.close()
                        raise e
                    yield (path, rel)
            zf.flush()
            zf.seek(0)
            yield (None, None)  # the end
            with CryptIO(dst, cipher, hashobj=hashobj) as fdst:
                copyfileobj(zf, fdst, 1024)
        dst.close()
    return (dst.name, _enc())
