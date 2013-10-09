from io import BufferedIOBase


class CryptIO(BufferedIOBase):

    def __init__(self, fileobj, cipher):
        if hasattr(fileobj, 'mode'):
            mode = fileobj.mode
        else:
            mode = 'wb'
        _m = mode[0:1]
        if _m != 'w' and _m != 'a':
            raise IOError("Mode '{}' not supported".format(mode))

        if not hasattr(fileobj, 'write'):
            raise ValueError("Invalid file object")

        if not hasattr(cipher, 'encipher'):
            raise ValueError("Invalid cipher object")

        self.fileobj = fileobj
        self.cipher = cipher

        self.offset = 0
        self.size = 0

    def _raise_if_closed(self):
        if self.closed:
            raise ValueError("I/O operation on closed file.")

    def write(self, data):
        self._raise_if_closed()

        # Convert data type if called by io.BufferedWriter.
        if isinstance(data, memoryview):
            data = data.tobytes()

        sz = len(data)
        if sz > 0:
            self.size += sz
            self.fileobj.write(self.cipher.encipher(data))
            self.offset += sz
        return sz

    def flush(self):
        self._raise_if_closed()
        self.fileobj.write(self.cipher.flush())
        self.fileobj.flush()

    def close(self):
        if self.closed:
            return
        super(CryptIO, self).close()
        self.fileobj = None

    def writable(self):
        return True
