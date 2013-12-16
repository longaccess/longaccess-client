from StringIO import StringIO
import hashlib


class HashIO(StringIO):
    def __init__(self):
        StringIO.__init__(self)
        self.md5 = hashlib.md5()

    def write(self, s):
        self.md5.update(s)

    def getvalue(self):
        return self.md5.digest()
