import os

from tempfile import mkstemp
from zipfile import ZipFile, ZIP_DEFLATED


def zip_writer(name, files, cache):
    fh, fname = mkstemp(prefix=name, dir=cache._cache_dir('tmp', write=True))
    zpf = ZipFile(os.fdopen(fh, 'w'), 'w', ZIP_DEFLATED, True)
    for f in files:
        zpf.write(f)
        yield f
    datadir = cache._cache_dir('data', write=True)
    zpf.close()
    os.rename(fname, os.path.join(datadir, name))
