from . import expected_text
from behave import step
from behave_cli import format_vars
from multiprocessing import Process
from importlib import import_module
from shutil import rmtree

import os
import pexpect
import fdpexpect
import pkg_resources
import sys
import shlex


@step(u'the environment variable "{name}" is "{value}"')
@format_vars
def env_var(context, name, value):
    context.environ[name] = value


@step(u'the home directory is "{directory}"')
def home_directory(context, directory):
    context.environ['HOME'] = directory
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            os.remove(directory)
        else:
            rmtree(directory)
        os.mkdir(directory)
    else:
        os.makedir(directory)
    assert os.path.isdir(directory), "Home directory doesn't exist"


@step(u'the command line arguments "{args}"')
@format_vars
def cli_args(context, args):
    context.args = args


@step(u'I run console script "{entry}"')
def run_console_script(context, entry):
    logfile = None
    if hasattr(context, 'stdout_capture'):
        logfile = context.stdout_capture

    e = None
    for p in pkg_resources.iter_entry_points(group='console_scripts'):
        if p.name == entry:
            e = p
    assert e, "Console script has entry point in setup.py"
    module = e.module_name
    target = e.attrs[0]

    def run_script(pipe, ctx):
        sys.stdout = os.fdopen(pipe, "w")
        sys.stderr = os.fdopen(pipe, "w")

        try:
            from features.steps import mp_setup
            mp_setup(ctx)
        except ImportError:
            pass
        try:
            from setproctitle import setproctitle
            setproctitle("console script {}".format(entry))
        except ImportError:
            pass
        for name, value in ctx.environ.iteritems():
            os.environ[name] = value
        os.chdir(ctx.cwd)
        sys.argv = ['-']
        if ctx.args:
            sys.argv += shlex.split(ctx.args)
        getattr(import_module(module), target)()

    me, pipe = os.pipe()
    proc = Process(target=run_script, args=(pipe, context))
    proc.start()

    context.child = fdpexpect.fdspawn(me, logfile=logfile)
    context.child.__proc = proc
    context.child.__pipe = me
    context.children[entry] = context.child


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
    txt = "Expected '{}'".format(text)
    assert expected_text(context.child, text, context.timeout), txt


@step(u'I wait until I don\'t see "{text}" anymore')
def wait_for_text(context, text):
    while expected_text(context.child, text, context.timeout):
        pass


@step(u'the timeout is {seconds} seconds')
def set_timeout(context, seconds):
    context.timeout = int(seconds)
