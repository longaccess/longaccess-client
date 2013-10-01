from testtools import TestCase
from mock import Mock
import json


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
            'json.side_effect': json,
            'raise_for_status': Mock(**kwargs),
        }
        return self._makesession(Mock(**mattr))

    def test_api(self):
        assert self._makeit()

    def test_api_root(self):
        r = json.loads(LA_ENDPOINTS_RESPONSE)
        s = self._makejson([r])
        api = self._makeit(url="http://baz.com/", session=s)
        self.assertEqual(r, api.root)
        s.get.assert_called_with("http://baz.com/")

    def test_no_capsules(self):
        caps = json.loads(LA_CAPSULES_RESPONSE)
        caps['objects'] = []
        caps['meta']['total_count'] = 0
        s = self._makejson([json.loads(LA_ENDPOINTS_RESPONSE), caps])
        api = self._makeit(url="http://baz.com/", session=s)
        capsules = api.get_capsules()
        self.assertEqual(len(capsules), 0)

    def test_capsules(self):
        r = map(json.loads, [LA_ENDPOINTS_RESPONSE, LA_CAPSULES_RESPONSE])
        s = self._makejson(r)
        api = self._makeit(url="http://baz.com/", session=s)
        capsules = api.get_capsules()
        self.assertEqual(len(capsules), 2)


LA_ENDPOINTS_RESPONSE = """{
  "account": {
     "list_endpoint": "/api/v1/account/",
     "schema": "/api/v1/account/schema/"
  },
  "archive": {
     "list_endpoint": "/api/v1/archive/",
     "schema": "/api/v1/archive/schema/"
  },
  "capsule": {
     "list_endpoint": "/api/v1/capsule/",
     "schema": "/api/v1/capsule/schema/"
  },
  "upload": {
     "list_endpoint": "/api/v1/upload/",
     "schema": "/api/v1/upload/schema/"
  }
}
"""

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
