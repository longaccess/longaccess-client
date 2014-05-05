import os

from testtools import TestCase
from . import makeprefs, MockLoggingHandler
from mock import Mock, patch


class RegistryTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(RegistryTest, cls).setUpClass()
        cls._lacli_log_handler = MockLoggingHandler(level='DEBUG')
        cls.lacli_log_messages = cls._lacli_log_handler.messages

    def setUp(self):
        super(RegistryTest, self).setUp()
        self.prefs = makeprefs(lambda x: None)
        self.home = os.path.join('t', 'data', 'home')
        self._lacli_log_handler.reset()
        from lacli.log import getLogger
        getLogger().addHandler(self._lacli_log_handler)

    def tearDown(self):
        super(RegistryTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.registry import LaRegistry
        return LaRegistry(*args, **kwargs)

    def test_registry(self):
        assert self._makeit(Mock(), self.prefs, Mock())

    def test_new_session(self):
        s = self.getUniqueString()
        f = Mock(return_value=s)
        prefs = makeprefs(f)
        r = self._makeit(Mock(), prefs, Mock())
        self.assertEqual(s, r.session)
        self.assertEqual(prefs['api'], f.call_args[0][0])

    @patch('lacli.registry.API_URL', new='http://wtf')
    def test_new_session_default_url(self):
        f = Mock()
        prefs = makeprefs(f)
        del prefs['api']['url']
        self._makeit(Mock(), prefs, Mock())
        self.assertEqual('http://wtf', f.call_args[0][0]['url'])

    def test_new_session_prefs(self):
        s = self.getUniqueString()
        f = Mock(return_value=s)
        myprefs = {self.getUniqueString(): self.getUniqueString()}
        r = self._makeit(Mock(), makeprefs(f), Mock())
        self.assertEqual(s, r.new_session(myprefs))
        self.assertEqual(myprefs, f.call_args[0][0])

    @patch('lacli.registry.netrc')
    def test_saved_session_error(self, netrc):
        f = Mock()
        prefs = makeprefs(f)
        prefs['api']['user'] = False
        exc = Exception(self.getUniqueString())
        netrc.side_effect = exc
        self._makeit(Mock(home='foo'), prefs, Mock())
        self.assertEqual(None, f.call_args[0][0]['pass'])
        self.assertEqual(os.path.expanduser('~/.netrc'),
                         netrc.call_args[0][0])
        for debug_msg, debug_exc in self.lacli_log_messages['debug']:
            self.assertIn("Couldn't read from netrc", debug_msg)
            self.assertTrue(debug_exc is not None)
            self.assertEqual(exc, debug_exc[1])
