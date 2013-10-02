from urlparse import urljoin
from latvm.tvm import BaseTvm
from lacli.log import getLogger
from lacli.decorators import cached_property, with_api_response

import json


API_URL = 'http://stage.longaccess.com/api/v1/'


class RequestsFactory():

    def __init__(self, prefs):
        self.prefs = prefs

    def new_session(self):
        import requests
        session = requests.Session()
        session.auth = (self.prefs['user'], self.prefs['pass'])
        return session


class Api(BaseTvm):

    def __init__(self, prefs, sessions=None):
        self.url = prefs['url']
        if self.url is None:
            self.url = API_URL
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

    def get_upload_token(self, secs=3600):
        token_url = self.endpoints['upload']
        getLogger().debug("requesting token from {}".format(token_url))
        return self._post(token_url, data=json.dumps({
            'title': 'test',
            'description': 'foobar',
            'capsule': '',
            'size': '',
        }))

    def tokens(self, secs=3600):
        while True:
            yield self.get_upload_token(secs=secs)

    def capsules(self):
        capsules_url = self.endpoints['capsule']
        return self._get(capsules_url)['objects']
