from .. import StorageConnection
from lacli.date import parse_timestamp, remaining_time
from lacli.log import getLogger
from lacli.decorators import cached_property
from boto import connect_s3
from boto.s3.key import Key


class S3Connection(StorageConnection):
    def __init__(self, token_access_key=None, token_secret_key=None,
                 token_session=None, token_expiration=None, bucket=None,
                 prefix='', **kwargs):
        super(S3Connection, self).__init__(**kwargs)
        self.accesskey = token_access_key
        self.secret = token_secret_key
        self.sectoken = token_session
        self.expires = token_expiration
        self._bucket = bucket
        self.prefix = prefix
        self.conn = None

    def getconnection(self):
        if self.conn is None:
            self.conn = connect_s3(
                aws_access_key_id=self.accesskey,
                aws_secret_access_key=self.secret,
                security_token=self.sectoken)
        return self.conn

    @cached_property
    def bucket(self):
        return self.getconnection().get_bucket(self._bucket)

    def newkey(self, key):
        return Key(self.bucket, self.prefix + key)

    def __getstate__(self):
        """ prepare the object for pickling. """
        state = self.__dict__
        state['conn'] = None
        return state

    def newupload(self, key):
        return self.bucket.initiate_multipart_upload(key)

    def complete_multipart(self, upload, etags):
        xml = '<CompleteMultipartUpload>\n'
        for seq, etag in enumerate(etags):
            xml += '  <Part>\n'
            xml += '    <PartNumber>{}</PartNumber>\n'.format(seq+1)
            xml += '    <ETag>{}</ETag>\n'.format(etag)
            xml += '  </Part>\n'
        xml += '</CompleteMultipartUpload>'
        return self.bucket.complete_multipart_upload(
            upload.key_name, upload.id, xml)


class MPConnection(S3Connection):
    def __init__(self, token_expiration=None, grace=120, **kwargs):
        super(MPConnection, self).__init__(**kwargs)
        self.grace = grace
        self.conn = None
        self.expiration = None
        if token_expiration is not None:
            try:
                self.expiration = parse_timestamp(token_expiration)
            except ValueError:
                getLogger().debug("invalid token expiration: %s",
                                  token_expiration)

    def timeout(self):
        """ return total number of seconds till
            this connection must be renewed. """
        if not self.expiration:
            return None
        remaining = remaining_time(self.expiration)
        return remaining.total_seconds() - self.grace
