from latvm.tvm import MyTvm
from boto.exception import NoAuthHandlerFound

class NoCredentialsException(Exception): pass

class UploadSession(object):

    def __init__(self, uid=None, secs=3600, bucket='lastage', retries=0, debug=0):
        self.uid=uid
        self.secs=3600

        try:
            self.tvm = MyTvm(bucket=bucket)
        except NoAuthHandlerFound as e:
            raise NoCredentialsException

    def tokens(self):
        while True:
            yield self.tvm.get_upload_token(uid=self.uid,
                                       secs=self.secs)
