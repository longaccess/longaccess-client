from testtools import TestCase
from mock import Mock


class AsyncTest(TestCase):
    def setUp(self):
        super(AsyncTest, self).setUp()

    def tearDown(self):
        super(AsyncTest, self).tearDown()

    def test_block_timeout(self):
        from lacli.async import block_timeout, TimeoutError, Failure
        from twisted.internet import defer, reactor

        c = defer.Deferred()
        errback = Mock(side_effect=c.callback)

        @block_timeout(1)
        def long():
            d = defer.Deferred()
            d.addErrback(errback)
            d.addCallback(Mock(side_effect=Exception()))
            reactor.callLater(3, d.callback, None)
            return d

        self.assertRaises(TimeoutError, long)

        @block_timeout(3)
        @defer.inlineCallbacks
        def check():
            try:
                yield c
            except defer.CancelledError:
                self.assertEqual(1, errback.call_count)
                self.assertEqual(1, len(errback.call_args[0]))
                a = errback.call_args[0][0]
                self.assertTrue(isinstance(a, Failure))
                self.assertEqual(a.type, defer.CancelledError)
            else:
                raise Exception("deferred was not cancelled")

        check()

    def test_block(self):
        from lacli.async import block
        from twisted.internet import defer, reactor, task

        d = defer.Deferred()

        @block
        def w():
            r = task.deferLater(reactor, 0.1, d.callback, None)
            self.assertFalse(d.called)
            return r
        w()
        self.assertTrue(d.called)
