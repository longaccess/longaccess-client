from behave import step
import os
import pexpect
import pipes


@step(u'the home directory is "{dir}"')
def home_directory(context, dir):
    context.environ['HOME'] = dir
    assert os.path.isdir(dir), "Home directory exists"


@step(u'I run "{command}"')
def run_command(context, command):
    run_named_command(context, command, '')


@step(u'I spawn "{command}" named "{name}"')
def run_named_command(context, command, name):
    context.children[name] = pexpect.spawn(
        command, cwd=context.cwd, env=context.environ)
    context.child = context.children[name]


@step(u'I see "{text}"')
def i_see_text(context, text):
    assert False
