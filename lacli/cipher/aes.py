from . import CipherBase
from Crypto.Cipher import AES
from Crypto.Util import Counter


class CipherAES(CipherBase):

    mode = 'aes-256-ctr'
    BLOCKSIZE = 16

    def __init__(self, cert, cipher=None):
        if not hasattr(cert, 'key') or len(cert.key) != self.BLOCKSIZE * 2:
            raise ValueError("Invalid cert and/or key")

        prefix = ''
        nbits = 128
        iv = 0L
        if cipher is not None and hasattr(cipher, 'input'):
            prefix = cipher.input[:8]    # NIST 800-38A
            iv = long(cipher.input[8:].encode('hex'), 16)
            nbits = 64

        self.ctr = Counter.new(nbits, prefix=prefix, initial_value=iv)
        self.obj = AES.new(cert.key, AES.MODE_CTR, counter=self.ctr)

    def encipher_block(self, block):
        # TODO we should let pycrypto do the block handling, it would be way
        # faster
        return self.obj.encrypt(block)

    def flush(self):
        last = super(CipherAES, self).flush()
        return self.obj.encrypt(last)
