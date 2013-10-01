import os
from behave import step
from tempfile import NamedTemporaryFile


@step(u'an empty file "{name}"')
def empty_file(context, name):
    if name not in context.files:
        context.files[name] = NamedTemporaryFile()
    context.file = context.files[name]
    assert os.path.exists(context.file.name), "Path exists"
    assert os.path.isfile(context.file.name), "Path is file"


@step(u'a file "{name}" with contents')
def file_with_content(context, name):
    empty_file(context, name)
    context.file.write(context.text)
