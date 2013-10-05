import os

from lacli.adf import make_adf, Archive, Meta
from behave import step
from tempfile import NamedTemporaryFile


@step(u'I have 1 prepared archive')
def one_archive(context):
    context.execute_steps(u'Given I have 1 prepared archive titled "foo"')


@step(u'I have 1 prepared archive titled "{title}"')
def one_archive_titled(context, title):
    d = os.path.join(context.environ['HOME'], ".longaccess/archives")
    if not os.path.isdir(d):
        os.makedirs(d)
    context.archive = NamedTemporaryFile(dir=d, suffix='.adf')
    context.archive.write(make_adf(Archive(title, Meta('zip', 'aes'))))
    context.archive.flush()
