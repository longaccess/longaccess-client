from __future__ import division

import os
import math

from sys import maxint
from itertools import imap
from tempfile import mkstemp
from boto.utils import compute_md5
from filechunkio import FileChunkIO


class FileHash(object):
    def __get__(self, instance, owner):
        try:
            return (instance.md5, instance.b64md5)
        except AttributeError:
            instance.seek(0)
            (instance.md5, instance.b64md5, size) = compute_md5(
                instance, instance.bytes)
            instance.seek(0)
            return (instance.md5, instance.b64md5)


class SavedPart(file):
    def __init__(self, source, num, *args, **kwargs):
        super(SavedPart, self).__init__(*args, **kwargs)
        self.bytes = source.chunksize(num)

    hash = FileHash()


class FilePart(FileChunkIO):

    def __init__(self, source, num, *args, **kwargs):
        super(FilePart, self).__init__(
            source.path, 'r',
            offset=source.chunkstart(num),
            bytes=source.chunksize(num), *args, **kwargs)

    hash = FileHash()


class ChunkedFile(object):
    minchunk = 5242880
    maxchunk = 104857600

    def __init__(self, path, skip=0, chunk=None):
        self.path = path
        self.isfile = os.path.isfile(path)
        size = maxint
        if self.isfile:
            size = os.path.getsize(path)
        assert size >= skip
        self.skip = skip
        self.size = size-skip
        self.chunk = chunk
        if self.chunk is None:
            self.chunk = min(max(int(self.size/100), self.minchunk),
                             self.maxchunk)
        self.chunks = int(math.ceil(self.size/self.chunk))
        if self.chunks == 0:
            self.chunks = 1

    def _savedchunks(self, tempdir):
        # split file and save parts to disk
        f = open(self.path, "rb")

        def _save(seq):
            b = f.read(self.chunk)
            if b:
                prefix = "part-{:>4}".format(seq)
                fh, fn = mkstemp(dir=tempdir, prefix=prefix)
                os.write(fh, b)
                os.close(fh)
                return fn
            f.close()

        return imap(_save, xrange(self.chunks))

    def chunkstart(self, num):
        return self.skip + num * self.chunk

    def chunksize(self, num):
        start = num * self.chunk
        if (start + self.chunk > self.size):
            # chunk end is EOF
            return self.size - start
        else:
            return self.chunk

    def chunkfile(self, seq, fname):
        if self.isfile:
            return FilePart(self, seq)
        else:
            return SavedPart(self, seq, fname)
