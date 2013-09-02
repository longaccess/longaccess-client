import requests


class RoboHydraTest(object):
    def __init__(self, name,
                 base="http://localhost:3000/robohydra-admin/tests/"):
        self.url = base + name
        self.action('start')

    def deactivate(self):
        self.action('stop')

    def action(self, act):
        requests.post(self.url, data={'action': act})


def cleanup(context):
    context.robohydra_tests = []
    context.robohydra_plugin = None


def setup(context):
    cleanup(context)


def teardown(context):
    for test in context.robohydra_tests:
        test.deactivate()
    cleanup(context)
