from behave import step
import os


@step(u'the home directory is "{dir}"')
def home_directory(context, dir):
    context.environ['HOME'] = dir
    assert os.path.isdir(dir), "Home directory exists"


@step(u'I run "{command}"')
def run_command(context, command):
    assert False


@step(u'I see "{text}"')
def i_see_text(context, text):
    assert False
