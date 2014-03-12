import sys
import os

from .zip import ZipArchiver
from lacli.enc import get_unicode
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


class FolderArchiver(ZipArchiver):
    def args(self, items, cb):
        if sys.platform.startswith('win'):
            # windows has unicode file system api
            items = imap(unicode, items)
        for path, rel in walk_folders(imap(os.path.abspath, items)):
            try:
                cb(path, rel)
                yield ((path,), {'arcname': rel.encode('utf-8')})
            except Exception as e:
                if not hasattr(e, 'filename'):
                    setattr(e, 'filename', path)
                raise
