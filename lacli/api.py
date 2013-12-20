from urlparse import urljoin
from lacli.log import getLogger
from lacli.decorators import cached_property, deferred_property, with_api_response, contains
from lacli.exceptions import ApiAuthException
from lacli.date import parse_timestamp
from lacli.defer_block import block
from contextlib import contextmanager
from twisted.internet import defer
from twisted.python import failure
from functools import partial

import json
import requests
import treq

from twisted.web.client import HTTPClientFactory
HTTPClientFactory.noisy = True


class TwistedRequestsFactory(object):
    def __init__(self):
        pass

    class TreqSession(object):
        auth = None
        verify = None
        

    class TwistedRequestsSession(object):
        def __init__(self, session):
            self.session = session

        @defer.inlineCallbacks
        def get(self, *args, **kwargs):
            try:
                r = yield treq.get(
                      *args, 
                      auth=self.session.auth,
                      **kwargs 
                  )
                getLogger().debug("response code : "+str(r.code))
                if r.code == 401:
                    raise ApiAuthException()
                r = yield treq.content(r)
                getLogger().debug("response: "+str(r))
                defer.returnValue(json.loads(r))
            except Exception as e:
                getLogger().debug("EXC: "+str(e))
                raise e

        @defer.inlineCallbacks
        def post(self, *args, **kwargs):
            r = yield treq.post(
                  *args, 
                  auth=self.session.auth,
                  **kwargs 
              )
            defer.returnValue(r)

        def patch(self, *args, **kwargs):
            return treq.patch(
                  *args, 
                  auth=self.session.auth,
                  **kwargs 
              )

    def __call__(self, prefs={}):
        session = self.TreqSession()
        if 'user' in prefs and 'pass' in prefs:
            session.auth = (prefs['user'], prefs['pass'])
        if 'verify' in prefs:
            session.verify = prefs['verify']
        return Api(prefs, self.TwistedRequestsSession(session))


class DummyResponse(object):
    def __init__(self, response):
        self.response = response

    def raise_for_status(self):
        pass

    def json(self):
        return self.response


class DummySession(object):
    def __init__(self, response_class):
        self.response_class = response_class
        self.get_response = {}

    def get(self, *args, **kwargs):
        return self.response_class(self.get_response)

    def post(self, *args, **kwargs):
        """ dummy post method """

    def patch(self, *args, **kwargs):
        """ dummy post method """


def DummyRequestsFactory(prefs={}):
    return DummySession(DummyResponse)


RequestsFactory = TwistedRequestsFactory()


class Api(object):

    def __init__(self, prefs, session=None):
        self.url = prefs.get('url')
        self.prefs = prefs
        self.session = session

    @deferred_property
    def root(self):
        getLogger().debug("requesting API root from {}".format(self.url))
        r = yield self._get(self.url)
        getLogger().debug("API root: {}".format(r))
        defer.returnValue(r)

    @deferred_property
    def endpoints(self):
        root = yield self.root
        r = yield dict(((n, urljoin(self.url, r['list_endpoint']))
                    for n, r in root.iteritems()))
        defer.returnValue(r)

    @defer.inlineCallbacks
    def _get(self, url):
        r = yield self.session.get(url.encode('utf8'))
        defer.returnValue(r)

    @defer.inlineCallbacks
    def _post(self, url, data=None):
        headers = {}
        if data is not None:
            headers['content-type'] = 'application/json'
        r = yield self.session.post(url, headers=headers, data=data)
        defer.returnValue(r)

    @defer.inlineCallbacks
    def _patch(self, url, data=None):
        headers = {}
        if data is not None:
            headers['content-type'] = 'application/json'
        r = yield self.session.patch(url, headers=headers, data=data)
        defer.returnValue(r)

    def _upload_status(self, uri, first=None):
        def parse(rsp):
            if rsp:
                if 'created' in rsp:
                    rsp['created'] = parse_timestamp(rsp['created'])
                if 'expires' in rsp:
                    rsp['expires'] = parse_timestamp(rsp['expires'])
                if 'archive' in rsp:
                    rsp['archive'] = urljoin(self.url, rsp['archive'])
            return rsp

        if first:
            yield parse(first)
        while True:
            yield parse(block(self._get(uri)))

    @contextmanager
    def upload(self, capsule, archive, auth=None):
        """
        Create an upload operation, provide the necessary info for transmission
        to storage, wrap up the upload operation at the end.

        >>> from lacli.adf import Archive, Meta, Auth
        >>> api = Api({}, DummyRequestsFactory())
        >>> meta = Meta('zip', 'xor')
        >>> archive = Archive('foo', meta)
        >>> auth = Auth(md5="foo")
        >>> with api.upload({'resource_uri': 'foo'}, archive, auth) as upload:
        ...     token = next(upload['tokens'])
        ...     uri = upload['uri']
        ...     id = upload['id']
        Traceback (most recent call last):
          File "/usr/local/lib/python2.7/doctest.py", line 1289, in __run
            compileflags, 1) in test.globs
          File "<doctest lacli.api.Api.upload[7]>", line 1, in <module>
            with uploader as upload:
          File "/usr/local/lib/python2.7/contextlib.py", line 17, in __enter__
            return self.gen.next()
          File "/home/kouk/code/longaccess-cli/lacli/api.py", line 137, in upload  # NOQA
            raise ValueError("No such capsule")
        ValueError: No such capsule
        """
        req_data = json.dumps(
            {
                'title': archive.title,
                'description': archive.description or '',
                'capsule': capsule['resource_uri']
            })
        status = block(self._post(self.endpoints['upload'], data=req_data))
        uri = urljoin(self.url, status['resource_uri'])
        account = block(self._get(self.endpoints['account']))
        yield {
            'tokens': self._upload_status(uri, status),
            'uri': uri,
            'account': account
        }
        patch = {'status': 'uploaded', 'size': archive.meta.size}
        if auth:
            patch['checksums'] = {}
            if hasattr(auth, 'sha512'):
                patch['checksums']['sha512'] = auth.sha512.encode("hex")
            if hasattr(auth, 'md5'):
                patch['checksums']['md5'] = auth.md5.encode("hex")
        block(self._patch(uri, data=json.dumps(patch)))

    def upload_status(self, uri):
        return next(self._upload_status(uri))

    @defer.inlineCallbacks
    def get_endpoint(self, name):
        endpoints = yield self.endpoints
        url = endpoints[name]
        getLogger().debug("requesting {} from {}".format(name, url))
        r = yield self._get(url)
        defer.returnValue(r)

    @defer.inlineCallbacks
    def async_capsules(self):
        r = yield self.get_endpoint('capsule')
        defer.returnValue(self.capsule_list(r))

    def capsules(self):
        return block(self.async_capsules())
        
    @contains(list)
    def capsule_list(self, cs):
        for c in cs.get('objects'):
            yield dict([(k, c.get(k, None))
                        for k in ['title', 'remaining', 'size',
                                  'id', 'resource_uri']])

    @contains(dict)
    def capsule_ids(self):
        for capsule in self.capsules():
            yield (capsule['id'], capsule)

    @deferred_property
    def async_account(self):
        r = yield self.get_endpoint('account')
        defer.returnValue(r)

    @cached_property
    def account(self):
        return block(self.async_account)
