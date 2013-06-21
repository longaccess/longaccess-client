from testtools import TestCase
from testtools.matchers import Equals

class TVMTest(TestCase):
    def _makeit(self, *args ,**kw):
        import test.tvm
        return test.tvm.mytvm(*args, **kw)

    def test_tvm(self):
        foo = self._makeit()

    def test_upload_token(self):
        tvm = self._makeit()
        token = tvm.get_upload_token('testuser1',3600)
        self.assertThat(token, Equals([]))
