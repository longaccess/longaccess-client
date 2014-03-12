import os
from . import Dumper
from tempfile import NamedTemporaryFile
from urllib import pathname2url
from lacli.adf import Links


class FileDumper(Dumper):
    tmpargs = {'delete': False,
               'suffix': ".longaccess"}

    def __init__(self, tmpdir='/tmp', home=None, **kwargs):
        super(FileDumper, self).__init__(**kwargs)
        self.tmpargs['dir'] = tmpdir
        self.home = home

    def update(self, result):
        super(FileDumper, self).update(result)
        path = self.path
        if self.home is not None:
            path = os.path.relpath(path, self.home)
        self.docs['links'] = Links(
            local=pathname2url(path))

    def write(self, data):
        self.dst.write(data)

    def __enter__(self):
        self.dst = NamedTemporaryFile(**self.tmpargs)
        self.path = self.dst.name
        return self

    def __exit__(self, eType, eValue, eTrace):
        try:
            super(FileDumper, self).__exit__(eType, eValue, eTrace)
        finally:
            self.dst.close()
            if eType is not None and os.path.exists(self.path):
                os.unlink(self.path)  # don't leave trash
