from behave_cli.api.mock import MockRestApi
import requests


class RoboHydraTest(object):

    def __init__(self, name, base):
        self.name = name
        self.base = base + "robohydra-admin/tests/"

    def start(self):
        self.action('start')

    def stop(self):
        self.action('stop')

    def action(self, act):
        url = self.base + self.name
        requests.post(url, data={'action': act})


class RoboHydra(MockRestApi):

    def __init__(self, *args, **kwargs):
        self.tests = {}
        super(RoboHydra, self).__init__(*args, **kwargs)

    def test(self, name):
        if name not in self.tests:
            self.tests[name] = RoboHydraTest(
                self.name+"/"+name,
                self.url())
        self.tests[name].start()

    def results(self):
        url = self.url() + "robohydra-admin/tests/results.json"
        result = requests.get(url)
        return result.json

    def close(self):
        for test in self.tests.iterkeys():
            self.tests[test].stop()
        self.tests = {}
        super(RoboHydra, self).close()
