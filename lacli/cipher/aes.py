from . import CipherBase


class CipherAES(CipherBase):

    mode = 'aes-256-ctr'

    def __init__(self, cert):
        pass

    def encipher(self, data):
        return data

    def flush(self):
        pass
