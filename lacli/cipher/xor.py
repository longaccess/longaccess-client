from . import CipherBase
from Crypto.Cipher import XOR


class CipherXOR(CipherBase):

    mode = 'xor'
    BLOCKSIZE = 8

    def __init__(self, key, input=None):
        if len(key) != self.BLOCKSIZE:
            raise ValueError("Invalid key")
        self.obj = XOR.new(key)

    def encipher_block(self, block):
        return self.obj.encrypt(block)

    def decipher_block(self, block):
        return self.obj.encrypt(block)

    def flush(self):
        last = super(CipherXOR, self).flush()
        return self.obj.encrypt(last)
