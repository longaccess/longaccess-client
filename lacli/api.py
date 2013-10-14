from urlparse import urljoin, urlparse
from lacli.log import getLogger
from lacli.decorators import cached_property, with_api_response, contains
from netrc import netrc
from contextlib import contextmanager

import json
import os


API_URL = 'https://www.longaccess.com/api/v1/'


class RequestsFactory():

    def __init__(self, prefs):
        self.prefs = prefs
        if self.prefs.get('user') is None:
            if os.path.exists(os.path.expanduser('~/.netrc')):
                self.read_netrc(self.prefs.get('url', API_URL))

    def new_session(self):
        import requests
        session = requests.Session()
        if 'user' in self.prefs and 'pass' in self.prefs:
            session.auth = (self.prefs['user'], self.prefs['pass'])
        if 'verify' in self.prefs:
            session.verify = self.prefs['verify']
        return session

    def read_netrc(self, url):
        if not url:
            return
        hostname = urlparse(url).hostname
        for host, creds in netrc().hosts.iteritems():
            if host == hostname:
                self.prefs['user'] = creds[0]
                self.prefs['pass'] = creds[2]


class Api(object):

    def __init__(self, prefs, sessions=None):
        self.url = prefs.get('url')
        if self.url is None:
            prefs['url'] = self.url = API_URL
        if sessions is None:
            sessions = RequestsFactory(prefs)
        self.session = sessions.new_session()

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
    def upload(self, capsule, archive):
        url = self.endpoints['capsule']
        cs = self._get(url)['objects']
        if capsule >= len(cs):
            raise ValueError("No such capsule")

        req_data = json.dumps(
            {
                'title': archive.title,
                'description': archive.description or '',
                'capsule': cs[capsule]['resource_uri'],
                'size': archive.meta.size,
            })
        status = self._post(self.endpoints['upload'], data=req_data)
        uri = urljoin(self.url, status['resource_uri'])
        yield {
            'tokens': self._upload_status(uri, status),
            'uri': uri,
            'id': status['id']
        }
        self._patch(uri, data=json.dumps({'status': 'uploaded'}))

    @contains(list)
    def capsules(self):
        url = self.endpoints['capsule']
        getLogger().debug("requesting capsules from {}".format(url))
        for cs in self._get(url)['objects']:
            yield dict([(k, cs.get(k, None))
                        for k in ['title', 'remaining', 'size']])
