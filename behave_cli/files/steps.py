import os
from behave import step
from tempfile import NamedTemporaryFile


@step(u'an empty file "{name}"')
def empty_file(context, name):
    assert name not in context.files
    f = NamedTemporaryFile()
    assert os.path.exists(f.name), "Path exists"
    assert os.path.isfile(f.name), "Path is file"
    context.files[name] = f


@step(u'a file "{name}" with contents')
def file_with_content(context, name):
    assert name not in context.files
    empty_file(context, name)
    context.files[name].write(context.text)
