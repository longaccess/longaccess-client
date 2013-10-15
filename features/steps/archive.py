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


@step(u'I have downloaded an archive containing "{folder}"')
def downloaded_archive(context, folder):
    prepare_archive_folder(context, folder)
    from glob import glob
    aglob = os.path.join(context.environ['HOME'], ".longaccess/archives/*")
    af = glob(aglob).pop()
    d = os.path.join(context.environ['HOME'], ".longaccess/certs")
    if not os.path.isdir(d):
        os.makedirs(d)
    from shutil import copy
    copy(af, d)


@step(u'I have {num} pending uploads')
def num_pending_uploads(context, num):
    for n in range(int(num)):
        pending_upload(context, "upload"+str(n))


@step(u'I have a pending upload titled "{title}"')
def pending_upload(context, title):
    prepare_archive(context, title)
    from glob import glob
    aglob = os.path.join(context.environ['HOME'], ".longaccess/archives/*")
    af = glob(aglob).pop()
    d = os.path.join(context.environ['HOME'], ".longaccess/uploads")
    if not os.path.isdir(d):
        os.makedirs(d)
    assert(context.mock_api)
    import urlparse
    url = urlparse.urljoin(context.mock_api.url(), 'path/to/api/upload/1')
    with open(af) as f:
        from lacli.adf import load_archive, make_adf
        docs = load_archive(f)
        docs['links'].upload = url
        with open(os.path.join(d, os.path.basename(af)), 'w') as out:
            make_adf(list(docs.itervalues()), out=out)


@step(u'the upload status is "{status}"')
def upload_status(context, status):
    if status == 'error':
        context.mock_api.test('uploadError', 'longaccessmock')
    elif status == 'completed':
        context.mock_api.test('uploadComplete', 'longaccessmock')


@step(u'there is a prepared archive titled "{title}"')
def exists_archive_titled(context, title):
    context.execute_steps(u"""
        Given the command line arguments "archive"
        When I run console script "lacli"
        Then I see ") {}"
        """.format(title))


@step(u'there is a completed certificate')
def exists_certificate(context):
    from glob import glob
    files = glob(os.path.join(context.environ['HOME'], ".longaccess/certs/*"))
    assert len(files) > 0, "there is a certificate"
    from lacli.adf import load_archive
    docs = {}
    with open(files[0]) as f:
        docs = load_archive(f)
    assert 'links' in docs
    assert 'archive' in docs
    assert hasattr(docs['links'], 'download')
    assert docs['links'].download == 'https://longaccess.com/yoyoyo'


@step(u'there are {num} pending uploads')
def pending_upload_num(context, num):
    from glob import glob
    aglob = os.path.join(context.environ['HOME'], ".longaccess/uploads/*")
    assert len(glob(aglob)) == int(num)


@step(u'I prepare an archive with a file "{title}"')
def prepare_archive(context, title):
    context.execute_steps(u'''
        Given an empty folder "{title}"
        And under "{{{title}}}" an empty file "{title}"
        And the command line arguments "archive  -t "{title}" {{{title}}}"
        When I run console script "lacli"
        Then I see "archive prepared"'''.format(title=title))


@step(u'I prepare an archive with a directory "{title}"')
def prepare_archive_folder(context, title):
    context.execute_steps(u'''
        Given the command line arguments "archive {title}"
        When I run console script "lacli"
        Then I see "archive prepared"'''.format(title=title))
