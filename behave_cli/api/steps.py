from behave_cli.api.robohydra import RoboHydra
from behave import step


@step(u'the API is failing')
def api_failing(context):
    context.mock_api.test('serverProblems')


@step(u'the mock API "{name}"')
def robohydra_api(context, name):
    context.mock_api = RoboHydra(name=name)
