from latvm.tvm import BaseTvm

import os
import requests


API_URL = 'http://stage.longaccess.com/api/v1/'


class ApiErrorException(Exception):
    pass


class ApiUnavailableException(Exception):
    pass


class Api(BaseTvm):

    root = None

    def __init__(self, url=None):
        if url is None:
            self.url = os.getenv('LA_API_URL')
        if self.url is None:
            self.url = API_URL

    def get_root(self):
        if self.root is None:
            try:
                self.root = self._get(self.url)
            except requests.exceptions.ConnectionError as e:
                raise ApiUnavailableException(e)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    raise ApiUnavailableException(e)
                else:
                    raise ApiErrorException(e)
        return self.root

    def _get(self, url):
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    def get_upload_token(self, uid=None, secs=3600):
        self.get_root()
