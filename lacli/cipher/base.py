from __future__ import division

import functools

from abc import ABCMeta, abstractmethod


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
        assert num < self.BLOCKSIZE, "plaintext padding error"
        return s[0:-num]
