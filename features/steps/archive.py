import os

from lacli.adf import make_adf, Archive, Meta, Links
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


@step(u'the archive has a link to a local copy')
def archive_copy(context):
    assert context.archive
    context.archive.write(make_adf(
        Links(local='file://' + os.path.join(context.environ['HOME'],
                                             ".longaccess/data"))))


@step(u'there is a prepared archive titled "{title}"')
def exists_archive_titled(context, title):
    context.execute_steps(u"""
        Given the command line arguments "archive"
        When I run console script "lacli"
        Then I see ") {}"
        """.format(title))
