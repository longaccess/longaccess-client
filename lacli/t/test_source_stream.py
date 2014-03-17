import os
from testtools import TestCase
from lacli.decorators import coroutine


class StreamSourceTest(TestCase):
    def setUp(self):
        super(StreamSourceTest, self).setUp()
        self.home = os.path.join('t', 'data', 'home')
        self.testfile = os.path.join('t', 'data', 'longaccess-74-5N93.html')

    def tearDown(self):
        super(StreamSourceTest, self).tearDown()

    def _makeit(self, *args, **kw):
        from lacli.source.stream import StreamSource
        return StreamSource(*args,  **kw)

    def test_constructor_none(self):
        self._makeit(None, None)

    def test_constructor_chunk(self):
        f = self._makeit(None, None, chunk=123)
        self.assertEqual(123, f.chunk)
        self.assertEqual(False, f.readable())
        self.assertEqual(True, f.writable())

    @coroutine
    def coro(self, *args):
        for v in args:
            v2 = yield
            yield self.assertEqual(v, v2)

    def test_write(self):
        vs = ["x"*50, "x"*50]
        f = self._makeit(self.coro(100), self.coro("x"*100))
        for v in vs:
            self.assertEqual(len(v), f.write(v))
        f.close()

    def test_write_context(self):
        with self._makeit(self.coro(100), self.coro("x"*100)) as f:
            self.assertEqual(50, f.write("x"*50))
            self.assertEqual(50, f.write("x"*50))

    def test_write_context2(self):
        with self._makeit(self.coro(0), self.coro("x"*100)) as f:
            f.close()

    def test_write_context3(self):
        with self._makeit(self.coro(0), self.coro("x"*100)) as f:
            f.close()
            self.assertRaises(ValueError, f.write, "BAR")

    def test_write_context4(self):
        with self._makeit(self.coro(90), self.coro("x"*90)) as f:
            self.assertEqual(50, f.write("x"*50))
            self.assertEqual(40, f.write("x"*40))

    def test_write_context5(self):
        with self._makeit(self.coro(90), self.coro("x"*90), chunk=90) as f:
            self.assertEqual(50, f.write("x"*50))
            self.assertEqual(40, f.write("x"*40))

    def test_write_context6(self):
        f = self._makeit(self.coro(90), self.coro("x"*90), chunk=90)
        f.dst = self.coro(None)
        e = self.assertRaises(Exception, f.close)
        self.assertEqual("Generator didn't stop", str(e))

    def test_write_context7(self):

        def mustraise():
            with self._makeit(self.coro(90), self.coro("x"*90)):
                raise Exception('lala')
        e = self.assertRaises(Exception, mustraise)
        self.assertEqual("lala", str(e))

        def catch():
            try:
                foo = yield
            except:
                foo = ''
            yield foo

        def mustraise2():
            with self._makeit(self.coro(90), self.coro("x"*90)) as f:
                f.end = catch()
                f.end.send(None)
                raise Exception('lala')
        e = self.assertRaises(Exception, mustraise2)
        self.assertEqual("Generator didn't stop after throw", str(e))
