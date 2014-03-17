from tempfile import NamedTemporaryFile
from lacli.adf import make_adf
from lacli.crypt import CryptIO
from lacli.cipher import get_cipher
from lacli.hash import HashIO
from shutil import copyfileobj
from zipfile import ZipFile
from abc import ABCMeta, abstractmethod


def archive_handle(docs):
    h = HashIO()
    make_adf(docs, out=h)
    return h.getvalue().encode('hex')


def restore_archive(archive, path, cert, folder, tmpdir, cb=None):
    cipher = get_cipher(archive, cert)
    with open(path, 'rb') as infile:
        with NamedTemporaryFile() as dst:
            with CryptIO(infile, cipher) as cf:
                copyfileobj(cf, dst)
            dst.flush()
            dst.seek(0)
            with ZipFile(dst) as zf:
                map(cb,
                    map(lambda zi: zf.extract(zi, folder), zf.infolist()))


class Archiver(object):
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        super(Archiver, self).__init__(**kwargs)

    @abstractmethod
    def args(self, items, cb=None):
        """ process each item before archiving, calling
            callback if supplied
        """

    @abstractmethod
    def archive(self, items, dest, cb):
        """ write every item to test and yield the item """
