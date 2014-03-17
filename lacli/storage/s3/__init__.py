from .. import StorageConnection
from lacli.date import parse_timestamp, remaining_time
from lacli.log import getLogger
from boto import connect_s3
from boto.s3.key import Key


class S3Connection(StorageConnection):
    def __init__(self, token_access_key=None, token_secret_key=None,
                 token_session=None, bucket=None, **kwargs):
        super(S3Connection, self).__init__(**kwargs)
        self.accesskey = token_access_key
        self.secret = token_secret_key
        self.sectoken = token_session
        self.bucket = bucket
        self.conn = None

    def getconnection(self):
        if self.conn is None:
            self.conn = connect_s3(
                aws_access_key_id=self.accesskey,
                aws_secret_access_key=self.secret,
                security_token=self.sectoken)
        return self.conn

    def getbucket(self):
        return self.getconnection().get_bucket(self.bucket)

    def newkey(self, key):
        return Key(self.getbucket(), key)

    def __getstate__(self):
        """ prepare the object for pickling. """
        state = self.__dict__
        state['conn'] = None
        return state


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
