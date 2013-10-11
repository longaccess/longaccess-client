import os

from lacli.adf import make_adf, Archive, Meta, Links, Certificate
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
    context.archive.write(make_adf(Archive(title, Meta('zip', 'aes-256-ctr'))))
    context.archive.flush()


@step(u'the archive titled "{title}" has a link to a local copy')
def archive_copy(context, title):
    assert context.archive
    context.archive.seek(0)
    context.archive.write(make_adf([
        Archive(title, Meta('zip', 'aes-256-ctr')),
        Links(local='file://' + os.path.join(context.environ['HOME'],
                                             ".longaccess/data/test"))]))
    context.archive.flush()


@step(u'the local copy for "{title}" is an empty file')
def archive_copy_empty(context, title):
    assert context.archive
    datadir = os.path.join(context.environ['HOME'], ".longaccess/data")
    if not os.path.exists(datadir):
        os.makedirs(datadir)
    with open(os.path.join(datadir, 'test'), 'w'):
        pass


@step(u'I have a certificate for the archive with title "{title}"')
def archive_cert(context, title):
    assert context.archive
    d = os.path.join(context.environ['HOME'], ".longaccess/certs")
    if not os.path.isdir(d):
        os.makedirs(d)
    context.cert = NamedTemporaryFile(dir=d, suffix='.adf')
    context.cert.write(make_adf([Archive(title, Meta('zip', 'aes-256-ctr')),
                                 Certificate()]))
    context.cert.flush()


@step(u'there is a prepared archive titled "{title}"')
def exists_archive_titled(context, title):
    context.execute_steps(u"""
        Given the command line arguments "archive"
        When I run console script "lacli"
        Then I see ") {}"
        """.format(title))


@step(u'I prepare an archive with a file "{title}"')
def prepare_archive(context, title):
    context.execute_steps(u'''
        Given an empty folder "foo"
        And under "{{foo}}" an empty file "{title}"
        And the command line arguments "archive {{foo}}"
        When I run console script "lacli"
        Then I see "archive prepared"'''.format(title=title))


@step(u'I prepare an archive with a directory "{title}"')
def prepare_archive_folder(context, title):
    context.execute_steps(u'''
        Given the command line arguments "archive {title}"
        When I run console script "lacli"
        Then I see "archive prepared"'''.format(title=title))
