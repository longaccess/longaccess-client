from testtools import TestCase
from mock import Mock


class SessionTest(TestCase):
    def setUp(self):
        super(SessionTest, self).setUp()

    def tearDown(self):
        super(SessionTest, self).tearDown()

    def _makeit(self, *args, **kw):
        from lacli.session import Session
        return Session(*args,  **kw)

    def test_session(self):
        assert self._makeit(api=Mock())

    def test_tokens(self):
        mattr = {'get_upload_token.side_effect': range(3)}
        api = Mock(**mattr)
        session = self._makeit(uid='foo', secs=0, api=api)
        tokens = session.tokens()
        for token in range(3):
            self.assertEqual(token, next(tokens))
        self.assertEqual(3, api.get_upload_token.call_count)
        api.get_upload_token.assert_called_with(secs=0)

    def test_no_capsules(self):
        mattr = {'get_capsules.return_value': []}
        api = Mock(**mattr)
        session = self._makeit(api=api)
        self.assertEqual([], session.capsules())
