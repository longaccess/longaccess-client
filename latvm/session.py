from latvm.tvm import MyTvm
from boto.exception import NoAuthHandlerFound
import os


class NoCredentialsException(Exception):
    pass


class Session(object):

    def __init__(self, uid=None, secs=3600, nprocs='auto',
                 bucket='lastage', retries=0, debug=0,
                 api=None, token_machine=None):
        self.uid = uid
        self.secs = 3600
        if api is None:
            self.api = os.getenv('LA_API_URL')
        else:
            self.api = api

        try:
            self.nprocs = int(nprocs)
        except ValueError:
            self.nprocs = None

        if token_machine is None:
            try:
                self.tvm = MyTvm(bucket=bucket)
            except NoAuthHandlerFound:
                raise NoCredentialsException
        else:
            self.tvm = token_machine

    def tokens(self):
        while True:
            yield self.tvm.get_upload_token(uid=self.uid,
                                            secs=self.secs)
