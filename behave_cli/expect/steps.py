from . import expected_text
from behave import step
from behave_cli.files.file import filename_vars
from behave_cli.vars import format_vars
from behave_cli.api import api_vars

import os
import pexpect
import pkg_resources


@step(u'the environment variable "{name}" is "{value}"')
@format_vars(filename_vars, api_vars)
def env_var(context, name, value):
    context.environ[name] = value


@step(u'the home directory is "{dir}"')
def home_directory(context, dir):
    context.environ['HOME'] = dir
    assert os.path.isdir(dir), "Home directory exists"


@step(u'the command line arguments "{args}"')
@format_vars(filename_vars)
def cli_args(context, args):
    context.args = args


@step(u'I run console script "{entry}"')
def run_console_script(context, entry):
    e = None
    for p in pkg_resources.iter_entry_points(group='console_scripts'):
        if p.name == entry:
            e = p
    assert e
    if entry is not None:
        run_named_command(
            context,
            "python -c 'from {m} import {f}; {f}()' {a}".format(
                m=e.module_name,
                f=e.attrs[0],
                a=(context.args or ''),
                ),
            ''
            )


@step(u'I run "{command}"')
def run_command(context, command):
    run_named_command(context, command, '')


@step(u'I spawn "{command}" named "{name}"')
def run_named_command(context, command, name):
    logfile = None
    if hasattr(context, 'stdout_capture'):
        logfile = context.stdout_capture
    context.children[name] = pexpect.spawn(
        command, cwd=context.cwd, env=context.environ,
        logfile=logfile)
    context.child = context.children[name]


@step(u'I see "{text}"')
def i_see_text(context, text):
    assert expected_text(context.child, text), "Expected '{}'".format(text)
