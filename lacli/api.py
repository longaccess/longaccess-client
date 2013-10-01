from urlparse import urljoin
from latvm.tvm import BaseTvm
from lacli.log import getLogger
from lacli.decorators import cached_property, with_api_response

import os
import requests
import json


API_URL = 'http://stage.longaccess.com/api/v1/'


class Api(BaseTvm):

    def __init__(self, url=None, session=None):
        if url is None:
            url = os.getenv('LA_API_URL')
        if url is None:
            url = API_URL
        self.url = url
        if session is None:
            self.session = requests.Session()
        else:
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

    def get_upload_token(self, uid=None, secs=3600):
        token_url = self.endpoints['upload']
        getLogger().debug("requesting token from {}".format(token_url))
        return self._post(token_url, data=json.dumps({
            'title': 'test',
            'description': 'foobar',
            'capsule': '',
            'size': '',
        }))

    def get_capsules(self, uid=None, pwd=None):
        capsules_url = self.endpoints['capsule']
        return self._get(capsules_url)
