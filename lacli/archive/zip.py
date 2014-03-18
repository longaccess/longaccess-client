from tempfile import NamedTemporaryFile
from zipfile import ZipFile, ZIP_DEFLATED
from shutil import copyfileobj
from contextlib import contextmanager
from . import Archiver

try:
    import zipstream
except ImportError:
    zipstream = None


class ZipArchiver(Archiver):
    def __init__(self, name=None, tmpdir='/tmp', **kwargs):
        super(ZipArchiver, self).__init__(**kwargs)
        if name is None:
            name = ''
        self.name = name
        self.tmpdir = tmpdir

    @contextmanager
    def _temp_file(self, fdst):
        with NamedTemporaryFile(prefix=self.name, dir=self.tmpdir) as zf:
            yield zf
            zf.flush()
            zf.seek(0)
            with fdst as dst:
                copyfileobj(zf, dst, 1024)

    def args(self, items, cb=None):
        for item in items:
            if cb is not None:
                cb(item, item)
            yield ((item,), {})

    def archive(self, items, dst, cb=None):

        if zipstream is None:
            # do it in two passes now as vanilla zipfile
            # can't easily handle streaming
            dst = self._temp_file(dst)

        with dst as zf:
            zipargs = {'mode': 'w', 'compression': ZIP_DEFLATED,
                       'allowZip64': True}
            if zipstream is None:
                with ZipFile(zf, **zipargs) as zpf:
                    for args, kwargs in self.args(items, cb):
                        yield zpf.write(*args, **kwargs)
            else:
                with zipstream.ZipFile(**zipargs) as zpf:
                    zpf.paths_to_write = self.args(items, cb)
                    for chunk in zpf:
                        yield zf.write(chunk)
