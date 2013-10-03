import os


# default URL
MOCK_API_URL = "http://localhost:3000/"


class MockRestApi(object):
    def __init__(self, name=None, base=None):
        if base is not None:
            self.base = base
        else:
            url = os.getenv('MOCK_API_URL')
            if url is not None:
                self.base = url
            else:
                self.base = MOCK_API_URL

        self.name = name

    def close(self):
        pass

    def url(self):
        return self.base
