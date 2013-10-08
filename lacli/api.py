from urlparse import urljoin, urlparse
from latvm.tvm import BaseTvm
from lacli.log import getLogger
from lacli.decorators import cached_property, with_api_response
from netrc import netrc

import json


API_URL = 'http://stage.longaccess.com/api/v1/'


class RequestsFactory():

    def __init__(self, prefs):
        self.prefs = prefs
        if self.prefs.get('user') is None:
            self.read_netrc(self.prefs.get('url', API_URL))

    def new_session(self):
        import requests
        session = requests.Session()
        session.auth = (self.prefs['user'], self.prefs['pass'])
        return session

    def read_netrc(self, url):
        if not url:
            return
        hostname = urlparse(url).hostname
        for host, creds in netrc().hosts.iteritems():
            if host == hostname:
                self.prefs['user'] = creds[0]
                self.prefs['pass'] = creds[2]


class Api(BaseTvm):

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

    def get_upload_token(self):
        token_url = self.endpoints['upload']
        getLogger().debug("requesting token from {}".format(token_url))
        return self._post(token_url, data=json.dumps({
            'title': 'test',
            'description': 'foobar',
            'capsule': '',
            'size': '',
        }))

    def tokens(self):
        while True:
            yield self.get_upload_token()

    def capsules(self):
        url = self.endpoints['capsule']
        keys = ['title', 'remaining', 'size']
        getLogger().debug("requesting capsules from {}".format(url))
        for cs in self._get(url)['objects']:
            yield dict([(k, cs.get(k, None)) for k in keys])
