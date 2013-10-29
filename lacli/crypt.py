from io import BufferedIOBase
from errno import EBADF
from lacli.exceptions import DecryptionError

READ, WRITE = 1, 2


class CryptIO(BufferedIOBase):

    def __init__(self, fileobj, cipher, mode=None, hashobj=None):
        if mode:
            mode = mode.replace('U', '')
        if mode and 'b' not in mode:
            mode += 'b'
        if mode is None:
            if hasattr(fileobj, 'mode'):
                mode = fileobj.mode
            else:
                mode = 'rb'
        _m = mode[0:1]
        if _m == 'r':
            self.mode = READ
            # From GzipFile:
            # Buffer data read from underlying file. extrastart is offset in
            # stream where buffer starts. extrasize is number of bytes
            # remaining in buffer from current stream position.
            self.extrabuf = ""
            self.extrasize = 0
            self.extrastart = 0
        elif _m == 'w' or _m == 'a':
            self.mode = WRITE
        else:
            raise IOError("Mode '{}' not supported".format(mode))

        if self.mode == WRITE and not hasattr(fileobj, 'write'):
            raise ValueError("Invalid file object")

        if self.mode == READ and not hasattr(fileobj, 'read'):
            raise ValueError("Invalid file object")

        if self.mode == WRITE and not hasattr(cipher, 'encipher'):
            raise ValueError("Invalid cipher object")

        if self.mode == READ and not hasattr(cipher, 'decipher'):
            raise ValueError("Invalid cipher object")

        self.fileobj = fileobj
        self.cipher = cipher

        self.offset = 0
        self.size = 0
        self.hashobj = hashobj

    def _raise_if_closed(self):
        if self.closed:
            raise ValueError("I/O operation on closed file.")

    def write(self, data):
        self._raise_if_closed()
        if self.mode != WRITE:
            raise IOError(EBADF, "write() on read-only CryptIO object")

        # Convert data type if called by io.BufferedWriter.
        if isinstance(data, memoryview):
            data = data.tobytes()

        sz = len(data)
        if sz > 0:
            self.size += sz
            towrite = self.cipher.encipher(data)
            self.fileobj.write(towrite)
            if self.hashobj:
                self.hashobj.update(towrite)
            self.offset += sz
        return sz

    def read(self, size=-1):
        self._raise_if_closed()
        if self.mode != READ:
            raise IOError(EBADF, "read() on write-only CryptIO object")

        _finished = lambda: size >= 0 and size <= self.extrasize

        def _add(data):  # put data into read buffer
            offset = self.offset - self.extrastart
            self.extrabuf = self.extrabuf[offset:] + data
            self.extrasize += len(data)
            self.extrastart = self.offset
            self.size += len(data)

        while not _finished():
            try:
                buf = self.fileobj.read(1024)
            except EOFError:
                buf = ""

            if len(buf) > 0:
                _add(self.cipher.decipher(buf))
            else:  # EOF
                _add(self.cipher.decipher('', True))
                if not _finished():
                    size = self.extrasize
                break

        start = self.offset - self.extrastart
        stop = start + size

        self.extrasize -= size
        self.offset += size

        return self.extrabuf[start:stop]

    def flush(self):
        self._raise_if_closed()
        if self.mode == WRITE:
            towrite = self.cipher.flush()
            if self.hashobj:
                self.hashobj.update(towrite)
            self.fileobj.write(towrite)
            self.fileobj.flush()

    def close(self):
        if self.closed:
            return
        super(CryptIO, self).close()
        self.fileobj = None

    def readable(self):
        return self.mode == READ

    def writable(self):
        return self.mode == WRITE

    def __exit__(self, eType, eValue, eTrace):
        if eType:
            raise DecryptionError(eValue)
