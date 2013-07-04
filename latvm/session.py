from latvm.tvm import MyTvm
from boto import config as boto_config
from boto.exception import NoAuthHandlerFound

class NoCredentialsException(Exception): pass

class UploadSession(object):

    def __init__(self, uid=None, secs=3600, bucket='lastage', retries=0, debug=0):
        self.uid=uid
        self.secs=3600
        if not boto_config.has_section('Boto'):
            boto_config.add_section('Boto')
        boto_config.set('Boto','num_retries', str(retries))
        if debug != 0:
            import multiprocessing as mp
            mp.util.log_to_stderr(mp.util.SUBDEBUG)
            boto_config.set('Boto','debug',str(debug))

        try:
            self.tvm = MyTvm(bucket=bucket)
        except NoAuthHandlerFound as e:
            raise NoCredentialsException

    def tokens(self):
        while True:
            yield self.tvm.get_upload_token(uid=self.uid,
                                       secs=self.secs)
