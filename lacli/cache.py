import os
import re

from glob import iglob
from itertools import imap
from lacli.adf import load_archive, Archive, make_adf
from lacli.log import getLogger
from unidecode import unidecode


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

    _slugify_strip_re = re.compile(r'[^\w\s-]')
    _slugify_hyphenate_re = re.compile(r'[-\s]+')

    @classmethod
    def _slugify(cls, value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        From Django's "django/template/defaultfilters.py".
        """
        if not isinstance(value, unicode):
            value = unicode(value)
        return unicode(cls._slugify_hyphenate_re.sub(
            '-', cls._slugify_strip_re.sub('', unidecode(value))
            ).strip().lower())

    def prepare(self, title):
        pass
