import sys
from io import BufferedIOBase


class StreamSource(BufferedIOBase):

    def __init__(self, dst, out, chunk=100):
        self.mode = 'w'
        self.end = dst
        self.out = out
        self.size = 0
        self.dst = self.sink()
        self.dst.send(None)
        self.buf = ""
        self.bufsize = 0
        self.chunk = chunk

    def sink(self):
        try:
            while True:
                data = yield
                if data is None:
                    break
                else:
                    self.out.send(data)
            self.end.send(self.size)
        except Exception as e:
            self.end.throw(e)
            raise Exception("Generator didn't stop after throw")

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
            newbuf = self.buf + data
            newbufsize = self.bufsize + sz
            while newbufsize >= self.chunk:
                self.size += self.chunk
                chunk = newbuf[:self.chunk]
                newbuf = newbuf[self.chunk:]
                newbufsize = newbufsize - self.chunk
                self.dst.send(chunk)
            self.buf = newbuf
            self.bufsize = newbufsize
        return sz

    def flush(self):
        self._raise_if_closed()
        if self.bufsize > 0:
            self.size += self.bufsize
            self.bufsize = 0
            self.dst.send(self.buf)
            self.buf = ''

    def close(self):
        if self.closed:
            return
        super(StreamSource, self).close()
        try:
            self.dst.send(None)
        except StopIteration:
            return
        else:
            raise Exception("Generator didn't stop")

    def readable(self):
        return False

    def writable(self):
        return True

    def __exit__(self, eType, eValue, eTrace):
        if eType is None:
            super(StreamSource, self).__exit__(eType, eValue, eTrace)
        else:
            try:
                self.dst.throw(eType, eValue, eTrace)
            except:
                if sys.exc_info()[1] is not eValue:
                    raise
            finally:
                self.bufsize = 0  # no point in flushing data anymore
                self.close()
