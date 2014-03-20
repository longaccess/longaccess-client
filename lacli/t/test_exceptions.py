from testtools import TestCase
from mock import patch


class ExceptionsTest(TestCase):
    def setUp(self):
        super(ExceptionsTest, self).setUp()

    def tearDown(self):
        super(ExceptionsTest, self).tearDown()

    def test_worker_failure(self):
        import lacli.exceptions
        with patch.object(lacli.exceptions, 'current_process',
                          create=True) as p:
            p.return_value = "foo"
            exc = lacli.exceptions.WorkerFailureError(Exception("lala"))
            self.assertEqual(p.call_count, 1)
            self.assertEqual("worker 'foo' failed", str(exc))
