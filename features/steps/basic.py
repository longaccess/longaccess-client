import os

from behave import step
from urlparse import urlparse


@step(u'I have 2 capsules')
def two_capsules(context):
    context.mock_api.test('oneCapsule', 'longaccessmock')


@step(u'I have 1 capsule')
def one_capsule(context):
    two_capsules(context)


@step(u'I have 1 huge capsule')
def one_huge_capsule(context):
    context.mock_api.test('oneHugeCapsule', 'longaccessmock')


@step(u'I have {num} uploaded archives')
def num_archives(context, num):
    if int(num) == 2:
        context.mock_api.test('twoArchives', 'longaccessmock')
    else:
        raise NotImplementedError("mock api only supports 2 archives")


@step(u'I store my credentials in "{file}"')
def my_store_in_netrc(context, file):
    assert(context.mock_api)
    p = urlparse(context.mock_api.url())
    context.execute_steps(u"""
        Given I store my credentials for "{}" in "{}"
        """.format(p.hostname, file))


@step(u'the Longaccess directory exists in HOME')
def make_longaccess(context):
    d = os.path.join(context.environ['HOME'], "Longaccess")
    if not os.path.isdir(d):
        os.makedirs(d)
