from testtools import TestCase, ExpectedException
from mock import Mock, patch
from . import makeprefs
from lacli.exceptions import ApiAuthException
import json


class ApiTest(TestCase):
    def setUp(self):
        super(ApiTest, self).setUp()
        self.prefs = makeprefs()['api']

    def tearDown(self):
        super(ApiTest, self).tearDown()

    def _makeit(self, *args, **kw):
        from lacli.api import Api
        return Api(*args, **kw)

    def _factory(self, prefs):
        from lacli.api import RequestsFactory
        return RequestsFactory(prefs)

    def _mocksessions(self, rsps):
        return Mock(new_session=Mock(return_value=Mock(**rsps)))

    def _mockresponse(self, json, method='get', **kwargs):
        mattr = {
            'json.side_effect': json,
            'raise_for_status': Mock(**kwargs),
        }
        return Mock(**mattr)

    def test_factory(self):
        import lacli.api
        mock_netrc = Mock(hosts={'bla.com': ('a', 'b', 'c')})
        mock_construct = Mock(return_value=mock_netrc)
        with patch.object(lacli.api, 'netrc', mock_construct, create=True):
            self._factory(self.prefs)
            self._factory({})
            self._factory({'url': None})
            f = self._factory({'url': 'http://bla.com'})
            self.assertEqual(f.prefs['user'], 'a')
            self.assertEqual(f.prefs['pass'], 'c')
            s = f.new_session()
            self.assertEqual(s.auth, ('a', 'c'))

    def test_api(self):
        assert self._makeit(self.prefs, Mock())

    def test_api_no_prefs(self):
        import lacli.api
        mock_netrc = Mock(hosts={'stage.longaccess.com': ('a', 'b', 'c')})
        mock_construct = Mock(return_value=mock_netrc)
        with patch.object(lacli.api, 'netrc', mock_construct, create=True):
            self._makeit({})
            self._makeit({}, self._factory({}))

    def test_api_root(self):
        r = json.loads(LA_ENDPOINTS_RESPONSE)
        s = self._mocksessions({'get.return_value': self._mockresponse([r])})
        api = self._makeit(self.prefs, sessions=s)
        self.assertEqual(r, api.root)

    def test_no_capsules(self):
        caps = json.loads(LA_CAPSULES_RESPONSE)
        caps['objects'] = []
        caps['meta']['total_count'] = 0
        r = self._mockresponse([json.loads(LA_ENDPOINTS_RESPONSE), caps])
        s = self._mocksessions({'get.return_value': r})
        api = self._makeit(self.prefs, sessions=s)
        capsules = list(api.capsules())
        self.assertEqual(len(capsules), 0)

    def test_capsules(self):
        j = map(json.loads, [LA_ENDPOINTS_RESPONSE, LA_CAPSULES_RESPONSE])
        s = self._mocksessions({'get.return_value': self._mockresponse(j)})
        api = self._makeit(self.prefs, sessions=s)
        capsules = list(api.capsules())
        self.assertEqual(len(capsules), 2)

    def test_unauthorized(self):
        from requests.exceptions import HTTPError
        exc = HTTPError(response=Mock(status_code=401))
        r = self._mockresponse({}, side_effect=exc)
        s = self._mocksessions({'get.return_value': r})
        api = self._makeit(self.prefs, sessions=s)
        with ExpectedException(ApiAuthException):
            list(api.capsules())

    def test_get_upload_token(self):
        er = self._mockresponse([json.loads(LA_ENDPOINTS_RESPONSE)])
        ur = self._mockresponse([json.loads(LA_UPLOAD_RESPONSE)])
        s = self._mocksessions({'get.return_value': er,
                               'post.return_value': ur})
        api = self._makeit(self.prefs, sessions=s)
        token = api.get_upload_token()
        self.assertIn('token_access_key', token)


LA_UPLOAD_RESPONSE = """{
    "id": 1,
    "capsule": "/api/v1/capsule/1/",
    "title": "foo",
    "description": "foo",
    "resource_uri": "/api/v1/upload/1/",
    "status": "pending",
    "token_access_key": "XXXXXXXXXXXXXXXXXXXX",
    "token_secret_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "token_session": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "token_expiration": "",
    "token_uid": "arn:aws:iam::XXXXXXXXXXXX:user/sts-test-dummy",
    "bucket": "lastage",
    "prefix": "prefix"
}
"""


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
