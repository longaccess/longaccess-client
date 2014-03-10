import os
import sys

from lacli.adf import Certificate, Archive, Meta, Links, Cipher
from lacli.archive.urls import dump_urls
from urllib import pathname2url


def prepare(title, urls, description=None, fmt='zip', cb=None):
    meta = Meta(fmt, Cipher('aes-256-ctr', 1))
    archive = Archive(title, meta, description=description),
    cert = Certificate(),
    name, path, auth = dump_urls(archive, urls, cert, cb)
    archive.meta.size = os.path.getsize(path)
    return {
        'archive': archive,
        'cert': cert,
        'links': Links(local=pathname2url(path)),
        'auth': auth
    }


if __name__ == "__main__":
    from lacli.adf import make_adf
    print make_adf(list(prepare('test', sys.argv[1:]).itervalues()))
