from . import RoboHydraTest
from behave import step


@step(u'the API is failing')
def home_directory(context):
    context.robohydra_tests.append(
        RoboHydraTest('{}/serverProblems'.format(
            context.robohydra_plugin)))


@step(u'the mock API "{plugin}"')
def robohydra_plugin(context, plugin):
    context.robohydra_plugin = plugin
