from urlparse import urljoin
from lacli import get_client_info
from lacli.decorators import cached_property, deferred_property, with_api_response, contains, block
from lacli.exceptions import ApiAuthException, UploadEmptyError, ApiUnavailableException, ApiErrorException
from lacli.date import parse_timestamp
from lacli.log import getLogger
from contextlib import contextmanager
from twisted.internet import defer
from twisted.python import failure
from functools import partial

import json
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
        def get_content(self, r):
            if r.code == 401:
                yield failure.Failure(ApiAuthException())
            if r.code == 404:
                yield failure.Failure(ApiUnavailableException())
            if r.code > 300:
                yield failure.Failure(ApiErrorException(
                    " ".join([str(r.code), str(r.phrase)])))
            r = yield treq.content(r)
            defer.returnValue(json.loads(r))

        def _defaults(self, kwds):
            defaults = { 
                'auth': self.session.auth,
                'persistent': False,
            }
            kwds.setdefault('headers', {}).update({
                'X-Longaccess-Agent': str(get_client_info()) })
            defaults.update(kwds)
            return defaults

        @defer.inlineCallbacks
        def get(self, *args, **kwargs):
            r = yield treq.get(*args, **self._defaults(kwargs))
            r = yield self.get_content(r)
            defer.returnValue(r)

        @defer.inlineCallbacks
        def post(self, *args, **kwargs):
            r = yield treq.post(*args, **self._default(kwargs))
            r = yield self.get_content(r)
            defer.returnValue(r)

        @defer.inlineCallbacks
        def patch(self, *args, **kwargs):
            r = yield treq.patch(*args, **self._default(kwargs))
            r = yield self.get_content(r)
            defer.returnValue(r)

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


class UploadOperation(object):
    uri = None

    def __init__(self, api, archive, capsule, uri):
        self.archive = archive
        self.capsule = capsule
        self.api = api
        self.uri = uri

    @defer.inlineCallbacks
    def start(self):
        endpoints = yield self.api.endpoints
        data = json.dumps( {
            'title': self.archive.title,
            'description': self.archive.description or '',
            'capsule': self.capsule['resource_uri'],
            'size': self.archive.meta.size
        })
        r = yield self.api._post(endpoints['upload'], data=data)
        self.uri = urljoin(self.api.url, r['resource_uri'])
        defer.returnValue(self.api.parse_status(r))

    @defer.inlineCallbacks
    def poll(self):
        r = yield self.api._get(self.uri)
        defer.returnValue(self.api.parse_status(r))

    @property
    def status(self):
        try:
            if self.uri is None:
                 return self.start()
            return self.poll()
        except Exception:
            getLogger().debug("Exception while getting status", exc_info=True)
            rause
          

    def finalize(self, auth=None, keys=[]):
        if self.uri is None:
            raise UploadEmptyError(
                reason="Attempt to finalize upload that hasn't started")
        patch = {'status': 'uploaded', 'size': self.archive.meta.size, 'parts': len(keys)}
        if auth is not None:
            patch['checksums'] = {}
            if hasattr(auth, 'sha512'):
                patch['checksums']['sha512'] = auth.sha512.encode("hex")
            if hasattr(auth, 'md5'):
                patch['checksums']['md5'] = auth.md5.encode("hex")
        return self.api._patch(self.uri, data=json.dumps(patch))


class Api(object):

    def __init__(self, prefs, session=None):
        self.url = prefs.get('url')
        self.prefs = prefs
        self.session = session

    @deferred_property
    def root(self):
        r = yield self._get(self.url)
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
        r = yield self.session.post(url.encode('utf8'), headers=headers, data=data)
        defer.returnValue(r)

    @defer.inlineCallbacks
    def _patch(self, url, data=None):
        headers = {}
        if data is not None:
            headers['content-type'] = 'application/json'
        r = yield self.session.patch(url.encode('utf8'), headers=headers, data=data)
        defer.returnValue(r)

    def upload(self, capsule, archive, state):
        uri = state.uri
        op = UploadOperation(self, archive, capsule, uri)
        return op

    def upload_cancel(self, state):
        pass

    @defer.inlineCallbacks
    def get_endpoint(self, name):
        endpoints = yield self.endpoints
        url = endpoints[name]
        r = yield self._get(url)
        defer.returnValue(r)

    @defer.inlineCallbacks
    def async_capsules(self):
        r = yield self.get_endpoint('capsule')
        defer.returnValue(self.capsule_list(r))

    def capsules(self):
        return block(self.async_capsules)()
        
    @contains(list)
    def capsule_list(self, cs):
        for c in cs.get('objects'): 
            ret = dict([(k, c.get(k, None))
                        for k in ['title', 'remaining', 'size',
                                  'id', 'resource_uri', 'created', 'expires']])
            ret['created'] = parse_timestamp(ret['created'])
            ret['expires'] = parse_timestamp(ret['expires'])
            yield ret

    @contains(dict)
    def capsule_ids(self):
        for capsule in self.capsules():
            yield (capsule['id'], capsule)

    @deferred_property
    def async_account(self):
        r = yield self.get_endpoint('account')
        defer.returnValue(r)

    @cached_property
    @block
    def account(self):
        return self.async_account

    @defer.inlineCallbacks
    def upload_status_async(self, uri):
        r = yield self._get(uri)
        defer.returnValue(self.parse_status(r))

    @block
    def upload_status(self, uri):
        return self.upload_status_async(uri)

    def parse_status(self, rsp):
        if rsp:
            if 'created' in rsp:
                rsp['created'] = parse_timestamp(rsp['created'])
            if 'expires' in rsp:
                rsp['expires'] = parse_timestamp(rsp['expires'])
            if 'archive' in rsp:
                rsp['archive'] = urljoin(self.url, rsp['archive'])
        return rsp
# vim: et:sw=4:ts=4
