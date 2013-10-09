from abc import ABCMeta, abstractmethod
from Crypto import Random


def cipher_modes():
    return dict([(c.mode, c) for c in CipherBase.__subclasses__()])


def new_key(nbit):
    return Random.new().read(32)


def get_cipher(archive, *args, **kwargs):
    return cipher_modes()[archive.meta.cipher.mode](*args, **kwargs)


class UnsupportedOperation(ValueError):
    pass


class CipherBase(object):
    __metaclass__ = ABCMeta

    def _unsupported(self, name):
        raise UnsupportedOperation("{}.{}() not supported".format(
            self.__class__.__name__, name))

    @abstractmethod
    def flush(self):
        pass

    def encipher(self, data):
        self._unsupported("encipher")


from . import aes  # NOQA
