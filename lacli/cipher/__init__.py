from abc import ABCMeta, abstractmethod
from Crypto import Random


def cipher_modes():
    return dict([(c.mode, c) for c in CipherBase.__subclasses__()])


def new_key(nbit):
    return Random.new().read(32)


def get_cipher(archive, *args, **kwargs):
    return cipher_modes()[archive.meta.cipher.mode](*args, **kwargs)


class CipherBase(object):
    __metaclass__ = ABCMeta

    BLOCKSIZE = 16
    _extra = ''

    @abstractmethod
    def flush(self):
        """ this must be called at the end of the encryption process """
        return self._pad(self._extra)

    def _buffer(self, data):
        total = len(data)
        if total > 0:
            blocksize = (self.BLOCKSIZE or 16)
            remaining = total
            while remaining >= blocksize:
                offset = total - remaining
                yield data[offset:(offset + blocksize)]
                remaining -= blocksize
            if remaining:
                self._extra = data[-remaining:]

    def encipher(self, data):
        ret = ''
        for block in self._buffer(self._extra + data):
            ret += self.encipher_block(block)
        return ret

    @abstractmethod
    def encipher_block(self, block):
        """ pipe a block of data through the cipher """

    def _pad(self, s, bs=None):
        """ pkcs7/rfc5652 padding """
        if bs is None:
            bs = self.BLOCKSIZE
        c = bs - len(s) % bs
        return s + chr(c) * c

    def _unpad(self, s):
        num = ord(s[-1])
        assert num < self.BLOCKSIZE
        return s[0:-num]

from . import aes  # NOQA
from . import xor  # NOQA
