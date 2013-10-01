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

    def test_capsules(self):
        mattr = {
            'json.return_value': LA_CAPSULES_RESPONSE,
            'raise_for_status': None,
        }
        mattr = {'get.return_value': Mock(**mattr)}
        s = Mock(**mattr)
        api = self._makeit(url="http://baz.com", session=s)
        capsules = api.get_capsules()
        self.assertEqual(len(capsules), 2)


LA_CAPSULES_RESPONSE = """{
  "meta": {
     "limit": 20,
     "next": null,
     "offset": 0,
     "previous": null,
     "total_count": 2
  },
  "objects": [
     {
         "created": "2013-06-07T10:45:01",
         "id": 3,
         "resource_uri": "/api/v1/capsule/3/",
         "title": "Photos",
         "user": "/api/v1/user/3/"
      },
      {
          "created": "2013-06-07T10:44:38",
          "id": 2,
          "resource_uri":
          "/api/v1/capsule/2/",
          "title": "Stuff",
          "user": "/api/v1/user/2/"
       }
    ]
}"""
