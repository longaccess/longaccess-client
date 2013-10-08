from testtools import TestCase
from mock import patch


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

    def test_worker_failure(self):
        import lacli.exceptions
        with patch.object(lacli.exceptions, 'current_process',
                          create=True) as p:
            p.return_value = "foo"
            exc = lacli.exceptions.WorkerFailureError(Exception("lala"))
            self.assertEqual(p.call_count, 1)
            self.assertEqual("worker 'foo' failed", str(exc))
