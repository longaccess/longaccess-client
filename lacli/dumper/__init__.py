from lacli.source.stream import StreamSource
from lacli.auth import MyHashObj
from lacli.decorators import coroutine
from lacli.adf import Certificate, Archive, Meta, Cipher
from lacli.cipher import get_cipher
from lacli.crypt import CryptIO
from abc import ABCMeta, abstractmethod


class Dumper(object):
    __metaclass__ = ABCMeta

    def __init__(self, docs={}, title='', description=None, fmt='zip',
                 hashf='sha512', chunk=100, **kwargs):
        self.hashobj = MyHashObj(hashf)
        self.chunk = chunk
        self.docs = docs
        if 'archive' not in self.docs:
            self.docs['archive'] = Archive(
                title, Meta(fmt, Cipher('aes-256-ctr', 1)),
                description=description)
        if 'cert' not in self.docs:
            self.docs['cert'] = Certificate()

    def update(self, result):
        self.docs.update(result)

    @abstractmethod
    def write(self, data):
        """ write a piece of data to the storage """

    @coroutine
    def uploader(self):
        while True:
            data = yield
            self.write(data)

    @coroutine
    def end(self):
        self.docs['archive'].meta.size = yield
        self.update({'auth': self.hashobj.auth()})

    def dump(self, items, cb):
        if not hasattr(self, 'archive'):
            raise NotImplementedError(
                "you need to inherit from an archiver class")
        with self:
            with StreamSource(self.end(), self.uploader(), self.chunk) as dest:
                cipher = get_cipher(self.docs['archive'], self.docs['cert'])
                fdst = CryptIO(dest, cipher, hashobj=self.hashobj)
                for result in self.archive(items, fdst, cb):
                    yield result

    def __enter__(self):
        return self

    def __exit__(self, eType, eValue, eTrace):
        return
