from behave_cli.api.mock import MockRestApi
import requests


class RoboHydraTest(object):

    def __init__(self, name, base, plugin):
        self.plugin = plugin
        self.name = name
        self.url = "{}robohydra-admin/scenarios/{}/{}".format(
            base, plugin, name)
        self.session = requests.Session()

    def start(self):
        self.action('start')

    def stop(self):
        self.action('stop')

    def action(self, act):
        self.session.post(self.url, data={'action': act})


class RoboHydra(MockRestApi):

    def __init__(self, *args, **kwargs):
        self.tests = {}
        self.session = requests.Session()
        super(RoboHydra, self).__init__(*args, **kwargs)

    def test(self, name, plugin):
        if name not in self.tests:
            self.tests[name] = RoboHydraTest(
                name,
                self.url(),
                plugin)
        self.tests[name].start()

    def results(self):
        url = self.url() + "robohydra-admin/rest/test-results/"
        result = self.session.get(url)
        return result.json()

    def close(self):
        for test in self.tests.iterkeys():
            self.tests[test].stop()
        self.tests = {}
        super(RoboHydra, self).close()
