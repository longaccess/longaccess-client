from behave import step
from urlparse import urlparse


@step(u'I have 1 capsule')
def one_capsule(context):
    context.mock_api.test('longaccessmock/oneCapsule')


@step(u'I store my credentials in "{file}"')
def my_store_in_netrc(context, file):
    assert(context.mock_api)
    p = urlparse(context.mock_api.url())
    context.execute_steps(u"""
        Given I store my credentials for "{}" in "{}"
        """.format(p.netloc, file))
