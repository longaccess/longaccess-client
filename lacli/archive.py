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


def dump_archive(archive, folder, cert, cb, tmpdir):
    name = "{}-{}".format(date.today().isoformat(),
                          _slugify(archive.title))
    files = (os.path.join(root, f)
             for root, _, fs in os.walk(folder)
             for f in fs)
    cipher = get_cipher(archive, cert)
    path, writer = _writer(name, files, cipher, tmpdir)
    map(cb, writer)
    return (name, path)


def _writer(name, files, cipher, tmpdir):
    path = os.path.join(tmpdir, name+".zip")

    def _enc(zf):
        print "Encrypting.."
        tmpargs = {'delete': False,
                   'dir': tmpdir}
        with NamedTemporaryFile(suffix=".crypt", **tmpargs) as dst:
            copyfileobj(zf, CryptIO(dst, cipher))
            os.rename(dst.name, path)
    return (path, _zip(name, files, tmpdir, _enc))


def _zip(name, files, tmpdir, enc=None):
    tmpargs = {'prefix': name,
               'dir': tmpdir}
    # do it in two passes now as zip can't easily handle streaming
    with NamedTemporaryFile(**tmpargs) as zf:
        with ZipFile(zf, 'w', ZIP_DEFLATED, True) as zpf:
            for f in files:
                zpf.write(f)
                yield f
        if enc:
            enc(zf)
