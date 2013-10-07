import os
import re

from glob import iglob
from itertools import imap
from lacli.adf import load_archive, Archive, Meta, make_adf
from lacli.log import getLogger
from unidecode import unidecode
from datetime import date


class Cache(object):
    def __init__(self, home):
        self.home = home

    def _cache_dir(self, path, write=False):
        dname = os.path.join(self.home, path)
        if not os.path.exists(dname) and write:
            os.makedirs(dname, mode=0744)
        return dname

    def _archive_open(self, name, mode='r'):
        dname = self._cache_dir('archives', write='w' in mode)
        return open(os.path.join(dname, name), mode)

    def archives(self):
        def getit(fn):
            with open(fn) as f:
                a = load_archive(f)
                if a:
                    return a
            getLogger().debug(
                "ADF file '{}' didn't contain archive description!".format(fn))
        fs = iglob(os.path.join(self._cache_dir('archives'), '*.adf'))
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
        adfname = "{}-{}.adf".format(
            date.today().isoformat(),
            Cache._slugify(title))
        with self._archive_open(adfname, 'w') as f:
            make_adf(Archive(title, Meta('', '')), out=f)
