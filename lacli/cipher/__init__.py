from Crypto import Random
from ..decorators import contains
from .base import CipherBase
from . import aes  # NOQA
from . import xor  # NOQA


@contains(dict)
def cipher_modes():
    for c in CipherBase.__subclasses__():
        yield (c.mode, c)


def new_key(nbit):
    return Random.new().read(32)


def get_cipher(archive, cert):
    """ return a suitable cipher object to decrypt/encrypt the archive
        using the certificate key and input parameters (iv, etc).
    """
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
