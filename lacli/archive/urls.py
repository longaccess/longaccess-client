import os
import types

from .zip import ZipArchiver
from urllib2 import urlopen


def enter(target, *args, **kwargs):
    return target


def exit(target, *args, **kwargs):
    pass


class UrlArchiver(ZipArchiver):
    def args(self, urls, cb):
        for url in urls:
            rel = os.path.basename(url.strip('/'))
            if cb is not None:
                cb(url, rel)
            r = urlopen(url)
            r.__enter__ = types.MethodType(enter, r)
            r.__exit__ = types.MethodType(exit, r)
            yield ((r,), {'arcname': rel.encode('utf-8')})
