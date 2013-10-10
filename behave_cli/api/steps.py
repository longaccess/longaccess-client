from behave_cli.api.robohydra import RoboHydra
from behave import step


@step(u'the API is failing')
def api_failing(context):
    context.mock_api.test('serverProblems', 'longaccessmock')


@step(u'the API authentication is wrong')
def api_auth_fail(context):
    context.mock_api.test('authFails', 'longaccessauth')


@step(u'the API authenticates a test user')
def api_auth_user(context):
    context.mock_api.test('authUser', 'longaccessauth')


@step(u'the mock API "{name}"')
def robohydra_api(context, name):
    context.mock_api = RoboHydra(name=name)
    for step in context.feature.parser.parse_steps(
            u"Then RoboHydra asserts do not fail"):
        context.scenario.steps.append(step)
        for formatter in context._runner.formatters:
            formatter.step(step)
            formatter.indentations.append(0)


@step(u'RoboHydra asserts do not fail')
def robohydra_asserts(context):
    rs = context.mock_api.results()
    for plugin, tests in rs.items():
        for test, test_results in tests.items():
            failures = test_results["failures"]
            assert len(failures) == 0, "test {} has failed".format(test)
