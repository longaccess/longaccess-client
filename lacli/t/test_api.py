from testtools import TestCase, ExpectedException
from mock import Mock, patch
from itertools import repeat, izip
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

    def _json_request(self, url, mock_call):
        args, kwargs = mock_call.call_args
        headers = kwargs['headers']
        self.assertEqual('application/json', headers['content-type'])
        self.assertEqual(url, args[0])
        return kwargs['data']

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
            self.assertEqual(s.verify, True)
            f = self._factory({'url': 'http://bla.com', 'verify': False})
            s = f.new_session()
            self.assertEqual(s.verify, False)

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

    def test_tokens_error(self):
        er = self._mockresponse([json.loads(LA_ENDPOINTS_RESPONSE)])
        caps = json.loads(LA_CAPSULES_RESPONSE)
        caps['objects'] = []
        caps['meta']['total_count'] = 0
        cr = self._mockresponse([caps])
        ur = self._mockresponse(repeat(json.loads(LA_UPLOAD_RESPONSE)))
        s = self._mocksessions({'get.side_effect': [er, cr],
                               'post.return_value': ur,
                               'patch.return_value': ur})
        api = self._makeit(self.prefs, sessions=s)
        tmgr = api.upload(1, Mock(title='', description=''))
        self.assertRaises(ValueError, tmgr.__enter__)

    def test_tokens(self):
        er = self._mockresponse([json.loads(LA_ENDPOINTS_RESPONSE)])
        cr = self._mockresponse([json.loads(LA_CAPSULES_RESPONSE)])
        ur = self._mockresponse(repeat(json.loads(LA_UPLOAD_RESPONSE)))
        post = Mock(return_value=ur)
        patch = Mock(return_value=ur)
        get = Mock(side_effect=[er, cr, ur, ur, ur, ur, Exception("foo")])
        s = self._mocksessions({'get': get, 'post': post, 'patch': patch})
        api = self._makeit(self.prefs, sessions=s)
        meta = Mock(size=1)
        auth = Mock(md5="foo", sha512="bar")
        tmgr = api.upload(1, Mock(title='', meta=meta, description=None), auth)
        url = 'http://baz.com/api/v1/upload/'
        with tmgr as upload:
            data = self._json_request(url, post)
            self.assertTrue('"description": ""' in data)
            self.assertTrue('"size": 1' in data)
            for seq, token in izip(xrange(4), upload['tokens']):
                self.assertIn('token_access_key', token)
        data = self._json_request(url+"1/", patch)
        self.assertTrue('"checksums": ' in data)
        self.assertTrue('"sha512": "bar"' in data)
        self.assertTrue('"md5": "foo"' in data)
        status = api.upload_status(url+"1/")
        self.assertTrue('status' in status)
        self.assertEqual('pending', status['status'])
        self.assertEqual(None, api.upload_status(url+"1/"))


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
