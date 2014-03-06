from testtools import TestCase, ExpectedException
from mock import Mock
from itertools import repeat
from . import makeprefs
from lacli.exceptions import ApiAuthException, ApiErrorException
from lacli.decorators import block
from twisted.internet import defer
from itertools import imap
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

    def _mocksessions(self, rsps):
        return Mock(**rsps)

    def _json_request(self, url, mock_call):
        args, kwargs = mock_call.call_args
        headers = kwargs['headers']
        self.assertEqual('application/json', headers['content-type'])
        self.assertEqual(url, args[0])
        return kwargs['data']

    def test_api(self):
        assert self._makeit(self.prefs, Mock())

    def test_api_root(self):
        r = json.loads(LA_ENDPOINTS_RESPONSE)
        s = self._mocksessions({'get.return_value': defer.succeed(r)})
        api = self._makeit(self.prefs, session=s)
        self.assertEqual(r, api.root)

    def test_no_capsules(self):
        caps = json.loads(LA_CAPSULES_RESPONSE)
        caps['objects'] = []
        caps['meta']['total_count'] = 0
        r = [defer.succeed(json.loads(LA_ENDPOINTS_RESPONSE)),
             defer.succeed(caps)]
        s = self._mocksessions({'get.side_effect': r})
        api = self._makeit(self.prefs, session=s)
        capsules = list(api.capsules())
        self.assertEqual(len(capsules), 0)

    def test_capsules(self):
        j = map(defer.succeed,
                map(json.loads, [LA_ENDPOINTS_RESPONSE, LA_CAPSULES_RESPONSE]))
        s = self._mocksessions({'get.side_effect': j})
        api = self._makeit(self.prefs, session=s)
        capsules = list(api.capsules())
        self.assertEqual(len(capsules), 2)

    def test_unauthorized(self):
        r = [defer.succeed(json.loads(LA_ENDPOINTS_RESPONSE)),
             defer.fail(ApiAuthException())]
        s = self._mocksessions({'get.side_effect': r})
        api = self._makeit(self.prefs, session=s)
        with ExpectedException(ApiAuthException):
            list(api.capsules())

    def test_status_start(self):
        _gets = map(defer.succeed,
                    map(json.loads,
                        [LA_ENDPOINTS_RESPONSE, LA_CAPSULES_RESPONSE]))
        _posts = imap(defer.succeed, repeat(json.loads(LA_UPLOAD_RESPONSE)))
        s = self._mocksessions({'get.side_effect': _gets,
                                'post.side_effect': _posts})
        api = self._makeit(self.prefs, session=s)
        state = Mock(uri=None)
        op = api.upload({'resource_uri': '/1'},
                        Mock(title='',
                             description='',
                             meta=Mock(size=1)), state)
        self.assertEqual(None, op.uri)
        block(lambda: op.status)()
        uri = 'http://baz.com/api/v1/upload/1/'
        self.assertEqual(uri, op.uri)

    def test_status_error(self):
        _gets = map(defer.succeed,
                    map(json.loads,
                        [LA_ENDPOINTS_RESPONSE, LA_CAPSULES_RESPONSE,
                         LA_UPLOAD_RESPONSE]))
        _gets.append(defer.fail(ApiErrorException()))
        _posts = imap(defer.succeed, repeat(json.loads(LA_UPLOAD_RESPONSE)))
        s = self._mocksessions({'get.side_effect': _gets,
                                'post.side_effect': _posts})
        api = self._makeit(self.prefs, session=s)
        state = Mock(uri=None)
        op = api.upload({'resource_uri': '/1'},
                        Mock(title='',
                             description='',
                             meta=Mock(size=1)), state)
        block(lambda: op.status)()
        block(lambda: op.status)()
        block(lambda: op.status)()
        self.assertRaises(ApiErrorException, block(lambda: op.status))


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

LA_EMPTY_COLLECTION = """{
  "meta": {
     "limit": 20,
     "next": null,
     "offset": 0,
     "previous": null,
     "total_count": 0
  },
  "objects": []
}"""
