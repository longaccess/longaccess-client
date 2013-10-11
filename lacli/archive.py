import os
import re

from unidecode import unidecode
from datetime import date
from tempfile import NamedTemporaryFile
from lacli.crypt import CryptIO
from lacli.cipher import get_cipher
from shutil import copyfileobj
from zipfile import ZipFile, ZIP_DEFLATED


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


def restore_archive(archive, path, cert, folder, tmpdir, cb=None):
    cipher = get_cipher(archive, cert)
    with open(path) as infile:
        with NamedTemporaryFile() as dst:
            with CryptIO(infile, cipher) as cf:
                copyfileobj(cf, dst)
            dst.flush()
            with ZipFile(dst) as zf:
                map(cb,
                    map(lambda zi: zf.extract(zi, folder), zf.infolist()))


def dump_archive(archive, folder, cert, cb=None, tmpdir='/tmp'):
    name = "{}-{}".format(date.today().isoformat(),
                          _slugify(archive.title))
    cipher = get_cipher(archive, cert)
    path, writer = _writer(name, os.path.abspath(folder), cipher, tmpdir)
    map(cb, writer)
    return (name, path)


def _writer(name, folder, cipher, tmpdir):
    path = os.path.join(tmpdir, name+".zip")

    def _enc(zf):
        print "Encrypting.."
        tmpargs = {'delete': False,
                   'dir': tmpdir}
        with NamedTemporaryFile(suffix=".crypt", **tmpargs) as dst:
            copyfileobj(zf, CryptIO(dst, cipher))
            os.rename(dst.name, path)
    return (path, _zip(name, folder, tmpdir, _enc))


def _zip(name, folder, tmpdir, enc=None):
    tmpargs = {'prefix': name,
               'dir': tmpdir}
    # do it in two passes now as zip can't easily handle streaming
    with NamedTemporaryFile(**tmpargs) as zf:
        with ZipFile(zf, 'w', ZIP_DEFLATED, True) as zpf:
            for root, _, fs in os.walk(folder):
                for f in (os.path.join(root, f) for f in fs):
                    path = os.path.join(root, f)
                    zpf.write(path, os.path.relpath(path, folder))
                    yield f
        if enc:
            zf.flush()
            zf.seek(0)
            enc(zf)
