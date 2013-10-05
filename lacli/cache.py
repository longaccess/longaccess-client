import os

from glob import iglob
from itertools import imap
from lacli.adf import load_archive
from lacli.log import getLogger


class Cache(object):
    def __init__(self, home):
        self.home = home

    def archives(self):
        def getit(fn):
            with open(fn) as f:
                a = load_archive(f)
                if a:
                    return a
            getLogger().debug(
                "ADF file '{}' didn't contain archive description!".format(fn))
        fs = iglob(os.path.join(self.home, 'archives', '*.adf'))
        return filter(None, imap(getit, fs))
