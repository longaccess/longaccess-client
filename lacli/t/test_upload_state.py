from testtools import TestCase
from mock import Mock


class UploadStateTest(TestCase):
    def setUp(self):
        from lacli.upload import UploadState
        UploadState.states = None
        super(UploadStateTest, self).setUp()

    def tearDown(self):
        super(UploadStateTest, self).tearDown()

    def _mockcache(self, uploads={}, archives={}):
        return Mock(_get_uploads=Mock(return_value=uploads),
                    _for_adf=Mock(return_value=archives))

    def test_no_uploads(self):
        from lacli.upload import UploadState
        UploadState.init(self._mockcache())
        archive = self.getUniqueString()
        self.assertEqual(archive, UploadState.get(archive).archive)
        self.assertTrue(archive in UploadState.states)

    def test_no_change_upload_size(self):
        from lacli.upload import UploadState
        UploadState.init(self._mockcache())
        archive = self.getUniqueString()
        size = 123
        self.assertEqual(size, UploadState.get(archive, size=size).size)
        e = self.assertRaises(AssertionError,
                              UploadState.get, archive, size=size+1)
        self.assertEqual("Can't change size for upload", str(e))

    def test_no_change_sandbox_status(self):
        from lacli.upload import UploadState
        UploadState.init(self._mockcache())
        archive = self.getUniqueString()
        self.assertFalse(UploadState.get(archive).sandbox)
        e = self.assertRaises(AssertionError,
                              UploadState.get, archive, sandbox=True)
        self.assertEqual("Can't change sandbox status for upload", str(e))

    def test_no_change_capsule(self):
        from lacli.upload import UploadState
        UploadState.init(self._mockcache())
        archive = self.getUniqueString()
        self.assertEqual(
            1, UploadState.get(archive, capsule={'id': 1}).capsule['id'])
        e = self.assertRaises(
            AssertionError, UploadState.get, archive, capsule={'id': 2})
        self.assertEqual("Can't change capsule for upload", str(e))

    def test_change_capsule(self):
        from lacli.upload import UploadState
        UploadState.init(self._mockcache())
        archive = self.getUniqueString()
        self.assertIs(None, UploadState.get(archive).capsule)
        self.assertEqual(
            2, UploadState.get(archive, capsule={'id': 2}).capsule['id'])
