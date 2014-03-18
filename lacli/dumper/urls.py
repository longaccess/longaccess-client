import sys

from lacli.adf.elements import Links
from lacli.adf.persist import make_adf
from lacli.archive.urls import UrlArchiver
from . import Dumper


class DummyDumper(Dumper, UrlArchiver):

    def __init__(self, **kwargs):
        super(DummyDumper, self).__init__(**kwargs)

    def update(self, result):
        super(DummyDumper, self).update(result)
        self.docs['links'] = Links()

    def write(self, data):
        print "dummy writing", len(data)


def prepare(title, urls, description=None, fmt='zip', cb=None):

    dest = DummyDumper(title=title, description=description, fmt=fmt)

    list(dest.dump(urls, cb))

    print make_adf(list(dest.docs.itervalues()))

if __name__ == "__main__":
    from lacli.log import setupLogging
    setupLogging(4)
    prepare('test', sys.argv[1:])
