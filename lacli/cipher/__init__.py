from Crypto import Random


modes = {
    'aes-256-ctr': None
}


def new_key(nbit):
    return Random.new().read(32)
