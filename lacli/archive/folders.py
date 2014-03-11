import sys
import os

from . import archive_handle
from .zip import writer as zip_writer
from lacli.enc import get_unicode
from lacli.cipher import get_cipher
from lacli.auth import MyHashObj
from itertools import imap


def walk_folders(folders):
    for folder in folders:
        if not os.path.isdir(folder):
            yield (folder, get_unicode(os.path.basename(folder)))
        else:
            for root, _, fs in os.walk(folder):
                for f in fs:
                    path = os.path.join(root, f)
                    strip = os.path.dirname(folder)
                    rel = os.path.relpath(path, strip)
                    yield (path, get_unicode(rel))


def args(items, cb):
    for path, rel in walk_folders(imap(os.path.abspath, items)):
        try:
            cb(path, rel)
            yield ((path,), {'arcname': rel.encode('utf-8')})
        except Exception as e:
            if not hasattr(e, 'filename'):
                setattr(e, 'filename', path)
            raise


def dump_folders(archive, items, cert, dst, cb=None, tmpdir='/tmp',
                 hashf='sha512'):
    name = archive_handle([archive, cert])
    cipher = get_cipher(archive, cert)
    hashobj = MyHashObj(hashf)

    if sys.platform.startswith('win'):
        # windows has unicode file system api
        items = map(unicode, items)

    zip_writer(name, args(items, cb),
               cipher, dst, tmpdir, hashobj)

    return (name, hashobj.auth())
