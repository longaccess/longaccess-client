import os
import shutil

from behave_cli import environment as clienv
from .steps import cert_vars


def before_all(context):
    clienv.before_all(context)
    if not hasattr(context, 'format_vars'):
        context.format_vars = []
    context.format_vars.append(cert_vars)


def after_all(context):
    clienv.after_all(context)


def before_feature(context, feature):
    clienv.before_feature(context, feature)


def after_feature(context, feature):
    clienv.after_feature(context, feature)


def before_scenario(context, scenario):
    clienv.before_scenario(context, scenario)
    context.archive = None
    context.cert = None
    context.certid = None
    context.certs = {}


def after_scenario(context, scenario):
    if context.archive is not None:
        context.archive.close()
    if context.cert is not None:
        context.cert.close()
    for cert, f in context.certs.iteritems():
        f.close()
    d = os.path.join(context.environ['HOME'], "Longaccess")
    if os.path.isdir(d):
        shutil.rmtree(d)
    clienv.after_scenario(context, scenario)
