import sys

from lacli.log import getLogger
from lacli.adf.elements import Links
from lacli.adf.persist import make_adf
from lacli.archive.urls import UrlArchiver
from lacli.storage.s3 import S3Connection
from . import Dumper
from StringIO import StringIO


class S3Dumper(Dumper, UrlArchiver):

    def __init__(self, key=None, retries=4, connection=None, **kwargs):
        kwargs['chunk'] = 10 * 1024 ** 3
        super(S3Dumper, self).__init__(**kwargs)
        self.connection = connection
        self.key = key
        if self.connection is None:
            self.connection = S3Connection()
        self.etags = []
        self.retries = retries
        self.seq = 0
        self.upload = None

    def update(self, result):
        super(S3Dumper, self).update(result)
        self.docs['links'] = Links()
        if self.upload is not None:
            key = self.connection.complete_multipart(self.upload, self.etags)
            self.docs['links'].upload = (key.key_name, key.etag)

    @property
    def bucket(self):
        return self.connection.getbucket()

    def write(self, data):
        sz = len(data)
        fp = StringIO(data)
        for attempt in range(self.retries):
            fp.seek(0)
            getLogger().debug("attempt %d/%d to transfer part %d",
                              attempt, self.retries, self.seq)

            try:
                key = self.upload.upload_part_from_file(
                    fp=fp,
                    part_num=self.seq+1,
                    size=sz
                )
                getLogger().debug("succesfully uploaded part %d: %s",
                                  self.seq, key)
                self.seq += 1
                self.etags.append(key.etag)
                break
            except Exception as exc:
                getLogger().debug("exception while uploading part %d",
                                  self.seq, exc_info=True)

                if attempt == self.retries-1:
                    raise exc

    def __enter__(self):
        if self.upload is None:
            self.upload = self.connection.newupload(self.key)
        return self

    def __exit__(self, eType, eValue, eTrace):
        super(S3Dumper, self).__exit__(eType, eValue, eTrace)
        if eType is not None:
            getLogger().debug("cancelling upload..", exc_info=True)
            if self.upload is not None:
                self.upload.cancel_upload()


def prepare(title, urls, bucket='uploads', description=None,
            fmt='zip', cb=None, **kwargs):

    c = S3Connection(bucket=bucket, **kwargs)

    dest = S3Dumper(connection=c, key='baz',
                    title=title, description=description, fmt=fmt)
    list(dest.dump(urls, cb))

    print make_adf(list(dest.docs.itervalues()))

if __name__ == "__main__":
    import os
    from lacli.log import setupLogging
    setupLogging(4)
    kwargs = {
        'host': os.environ.get('S3_HOST'),
        'port': os.environ.get('S3_PORT'),
        'is_secure': os.environ.get('S3_SECURE', False)
    }
    c = S3Connection(**kwargs)
    c.getconnection().create_bucket('foo')
    prepare('test', sys.argv[1:], bucket='foo', **kwargs)
