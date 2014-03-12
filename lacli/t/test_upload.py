from testtools import TestCase
from mock import Mock


class UploadTest(TestCase):
    def setUp(self):
        super(UploadTest, self).setUp()

    def tearDown(self):
        super(UploadTest, self).tearDown()

    def _makeit(self, *args, **kw):
        from lacli.upload import Upload
        return Upload(*args,  **kw)

    def test_upload(self):
        assert self._makeit(Mock(), 4, 4, Mock())
