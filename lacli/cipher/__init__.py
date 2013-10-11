from __future__ import division

import functools

from abc import ABCMeta, abstractmethod
from Crypto import Random
from ..decorators import contains


@contains(dict)
def cipher_modes():
    for c in CipherBase.__subclasses__():
        yield (c.mode, c)


def new_key(nbit):
    return Random.new().read(32)


def get_cipher(archive, cert):
    input = None
    key = None
    cipher = archive.meta.cipher
    if hasattr(cipher, 'input'):
        input = cipher.input
    if hasattr(cert, 'key'):
        key = cert.key
    elif hasattr(cert, 'keys') and len(cert.keys) > 0:
        if hasattr(cipher, 'key'):
            idx = cipher.key
            if idx > 0 and idx <= len(cert.keys):
                key = cert.keys[idx-1]
        else:
            key = cert.keys[0]
    mode = None
    if hasattr(cipher, 'mode'):
        mode = cipher.mode
    elif isinstance(cipher, str):
        mode = cipher
    if mode:
        cipher_class = cipher_modes().get(mode)
        if cipher_class:
            return cipher_class(key, input)


class CipherBase(object):
    __metaclass__ = ABCMeta

    BLOCKSIZE = 16
    _extra = ''

    @abstractmethod
    def flush(self):
        """ this must be called at the end of the encryption process """
        return self._pad(self._extra)

    def _buffer(self, data, last=False):
        data = self._extra + data
        total = len(data)
        nblocks = total // self.BLOCKSIZE
        if last:
            nblocks -= 1
        pos = 0
        for i in range(nblocks):
            yield data[pos:pos + self.BLOCKSIZE]
            pos += self.BLOCKSIZE
        self._extra = data[pos:]

    def _reduce(self, func, blocks):
        return functools.reduce(lambda r, b: r + func(b), blocks, '')

    def encipher(self, data):
        return self._reduce(self.encipher_block, self._buffer(data))

    def decipher(self, data, last=False):
        ret = self._reduce(self.decipher_block, self._buffer(data, True))
        if last and len(self._extra) > 0:
            if len(self._extra) != self.BLOCKSIZE:
                raise ValueError("Total input not a multiple of blocksize")
            ret += self._unpad(self.decipher_block(self._extra))
            self._extra = ''
        return ret

    @abstractmethod
    def encipher_block(self, block):
        """ pipe a block of data through the cipher """

    @abstractmethod
    def decipher_block(self, block):
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
