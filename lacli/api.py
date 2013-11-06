from urlparse import urljoin
from lacli.log import getLogger
from lacli.decorators import cached_property, with_api_response, contains
from contextlib import contextmanager

import json


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


def RequestsFactory(prefs={}):
    import requests
    session = requests.Session()
    if 'user' in prefs and 'pass' in prefs:
        session.auth = (prefs['user'], prefs['pass'])
    if 'verify' in prefs:
        session.verify = prefs['verify']
    return Api(prefs, session)


class Api(object):

    def __init__(self, prefs, session=None):
        self.url = prefs.get('url')
        self.session = session

    @cached_property
    def root(self):
        return self._get(self.url)

    @cached_property
    def endpoints(self):
        return dict(((n, urljoin(self.url, r['list_endpoint']))
                    for n, r in self.root.iteritems()))

    @with_api_response
    def _get(self, url):
        return self.session.get(url)

    @with_api_response
    def _post(self, url, data=None):
        headers = {}
        if data is not None:
            headers['content-type'] = 'application/json'
        return self.session.post(url, headers=headers, data=data)

    @with_api_response
    def _patch(self, url, data=None):
        headers = {}
        if data is not None:
            headers['content-type'] = 'application/json'
        return self.session.patch(url, headers=headers, data=data)

    def _upload_status(self, uri, first=None):
        if first:
            yield first
        while True:
            yield self._get(uri)

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
        >>> with api.upload(1, archive, auth) as upload:
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
        cs = []
        if 'capsule' in self.endpoints:
            url = self.endpoints['capsule']
            cs = self._get(url).get('objects', [])
        if capsule >= len(cs):
            raise ValueError("No such capsule")

        req_data = json.dumps(
            {
                'title': archive.title,
                'description': archive.description or '',
                'capsule': cs[capsule]['resource_uri']
            })
        status = self._post(self.endpoints['upload'], data=req_data)
        uri = urljoin(self.url, status['resource_uri'])
        account = self._get(self.endpoints['account'])
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
        self._patch(uri, data=json.dumps(patch))

    def upload_status(self, uri):
        return next(self._upload_status(uri))

    @contains(list)
    def capsules(self):
        url = self.endpoints['capsule']
        getLogger().debug("requesting capsules from {}".format(url))
        for cs in self._get(url)['objects']:
            yield dict([(k, cs.get(k, None))
                        for k in ['title', 'remaining', 'size']])

    @cached_property
    def account(self):
        return self._get(self.endpoints['account'])
