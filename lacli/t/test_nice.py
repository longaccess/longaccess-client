from testtools import TestCase
from mock import patch, call


class NiceTest(TestCase):
    @patch('psutil.Process')
    def test_nice(self, proc):
        from lacli.nice import with_low_priority

        @with_low_priority
        def fun(foo, bar=None):
            self.assertEqual('lala', foo)
            self.assertEqual('barf', bar)
            return 'lol'

        proc.return_value.nice.return_value = 'original'
        with patch('psutil.BELOW_NORMAL_PRIORITY_CLASS',
                   new='class', create=True):
            self.assertEqual('lol', fun('lala', bar='barf'))
        proc.assert_called()
        proc.return_value.nice.assert_has_calls(
            [call(), call('class'), call('original')])
        proc.return_value.reset_mock()
        self.assertEqual('lol', fun('lala', bar='barf'))
        proc.return_value.nice.assert_has_calls(
            [call(), call(20), call('original')])
