from testtools import TestCase


class ExceptionsTest(TestCase):
    def setUp(self):
        super(ExceptionsTest, self).setUp()

    def tearDown(self):
        super(ExceptionsTest, self).tearDown()

    def _makeit(self, *args, **kw):
        from lacli.exceptions import BaseAppException
        return BaseAppException(*args, **kw)

    def test_exception(self):
        assert self._makeit(Exception())

    def test_str(self):
        exc = self._makeit(Exception("lala"))
        exc.msg = "foobar"
        self.assertEqual("foobar", str(exc))
