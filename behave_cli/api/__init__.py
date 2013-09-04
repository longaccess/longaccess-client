import requests


MOCK_API_BASE = "http://localhost:3000/"


def api_vars(ctx):
    return dict([(ctx.robohydra_plugin, MOCK_API_BASE)])


class RoboHydraTest(object):
    def __init__(self, name,
                 base="robohydra-admin/tests/"):
        self.url = MOCK_API_BASE + base + name
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
