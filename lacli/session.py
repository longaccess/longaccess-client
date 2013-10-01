from lacli.api import Api


class NoCredentialsException(Exception):
    pass


class Session(object):

    def __init__(self, uid=None, pwd=None, secs=3600, nprocs='auto',
                 bucket='lastage', retries=0, debug=0,
                 api=None):
        self.uid = uid
        self.pwd = pwd
        self.secs = secs
        try:
            self.nprocs = int(nprocs)
        except ValueError:
            self.nprocs = None
        if api is None:
            self.api = Api()
        else:
            self.api = api

    def tokens(self):
        while True:
            yield self.api.get_upload_token(uid=self.uid,
                                            secs=self.secs)

    def capsules(self):
        return self.api.get_capsules(uid=self.uid, pwd=self.pwd)
