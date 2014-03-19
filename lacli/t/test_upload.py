from testtools import TestCase
from mock import Mock, MagicMock
from lacli.async import block


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

    def test_no_file(self):
        upload = self._makeit(Mock(), 4, 4, MagicMock())
        f = block(upload.upload)

        e = self.assertRaises(IOError, f, 'lala', MagicMock(), MagicMock())
        self.assertEqual("File lala not found", str(e))
