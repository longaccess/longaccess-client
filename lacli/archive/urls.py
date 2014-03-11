import os
import types

from . import archive_handle
from .zip import writer as zip_writer
from lacli.cipher import get_cipher
from lacli.auth import MyHashObj
from urllib2 import urlopen


def enter(target, *args, **kwargs):
    return target


def exit(target, *args, **kwargs):
    pass


def args(urls, cb):
    for url in urls:
        rel = os.path.basename(url.strip('/'))
        cb(url, rel)
        r = urlopen(url)
        r.__enter__ = types.MethodType(enter, r)
        r.__exit__ = types.MethodType(exit, r)
        yield ((r,), {'arcname': rel.encode('utf-8')})


def dump_urls(archive, urls, cert, cb=None, tmpdir='/tmp',
              hashf='sha512'):
    name = archive_handle([archive, cert])
    cipher = get_cipher(archive, cert)
    hashobj = MyHashObj(hashf)

    path = zip_writer(name, args(urls, cb),
                      cipher, tmpdir, hashobj)

    return (name, path, hashobj.auth())
