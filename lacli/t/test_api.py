from testtools import TestCase
from mock import Mock


class ApiTest(TestCase):
    def setUp(self):
        super(ApiTest, self).setUp()

    def tearDown(self):
        super(ApiTest, self).tearDown()

    def _makeit(self, *args, **kw):
        from lacli.api import Api
        return Api(*args, **kw)

    def _makesession(self, rsp, method='get'):
        mattr = {method+'.return_value': rsp}
        return Mock(**mattr)

    def _makejson(self, json, **kwargs):
        mattr = {
            'json.return_value': json,
            'raise_for_status': Mock(**kwargs),
        }
        return self._makesession(Mock(**mattr))

    def test_api(self):
        assert self._makeit()

    def test_api_root(self):
        s = self._makejson('lala')
        api = self._makeit(url="http://baz.com/", session=s)
        self.assertEqual("lala", api.root)
        s.get.assert_called_with("http://baz.com/")
