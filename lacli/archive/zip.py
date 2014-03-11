from tempfile import NamedTemporaryFile
from lacli.crypt import CryptIO
from zipfile import ZipFile, ZIP_DEFLATED
from shutil import copyfileobj
from contextlib import contextmanager

try:
    import zipstream
except ImportError:
    zipstream = None


@contextmanager
def _temp_file(fdst, name, tmpdir):
    with NamedTemporaryFile(prefix=name, dir=tmpdir) as zf:
        yield zf
        zf.flush()
        zf.seek(0)
        with fdst as dst:
            copyfileobj(zf, dst, 1024)


def writer(name, args, cipher, dst, tmpdir, hashobj=None):

    fdst = CryptIO(dst, cipher, hashobj=hashobj)

    if zipstream is None:
        # do it in two passes now as vanilla zipfile
        # can't easily handle streaming
        fdst = _temp_file(fdst, name, tmpdir)

    with fdst as zf:
        zipargs = {'mode': 'w', 'compression': ZIP_DEFLATED,
                   'allowZip64': True}
        if zipstream is None:
            with ZipFile(zf, **zipargs) as zpf:
                for args, kwargs in args:
                    zpf.write(*args, **kwargs)
        else:
            with zipstream.ZipFile(**zipargs) as zpf:
                zpf.paths_to_write = args
                for chunk in zpf:
                    zf.write(chunk)
