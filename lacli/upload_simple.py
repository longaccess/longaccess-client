import sys
import os

from lacli.decorators import block
from twisted.internet import defer
from lacli.adf import Archive, Meta, Cipher, make_adf
from lacli.api import RequestsFactory, UploadOperation
from lacli.storage.s3 import S3Connection
from lacli.dumper.s3 import S3Dumper


API_URL = 'https://www.longaccess.com/api/v1/'


@block
@defer.inlineCallbacks
def upload(title, urls, description=None,
           fmt='zip', capsule=None, cb=None, **kwargs):

    api = RequestsFactory({'user': 'test', 'pass': 'test',
                           'url': os.getenv('LA_API_URL', API_URL)})
    cs = yield api.async_capsules()
    for c in cs:
        if c['id'] == int(capsule):
            capsule = c
            break
    else:
        raise RuntimeError("capsule {} not found".format(capsule))
    archive = Archive(title, Meta(fmt, Cipher('aes-256-ctr', 1)),
                      description=description)
    op = UploadOperation(api, archive, capsule, None)
    status = yield op.status
    c = S3Connection(**status)

    dest = S3Dumper(connection=c, key='upload-temp',
                    docs={'archive': archive})
    list(dest.dump(urls, cb))
    dest.docs['links'].upload = op.uri
    account = yield api.async_account
    dest.docs['archive'].meta.email = account['email']
    dest.docs['archive'].meta.name = account['displayname']
    c.newkey('certificate.adf').set_contents_from_string(
        make_adf(list(dest.docs.itervalues())))
    yield op.finalize(dest.docs['auth'], dest.etags)


if __name__ == "__main__":
    from lacli.log import setupLogging
    setupLogging(4)
    upload('test', sys.argv[2:], capsule=sys.argv[1])
