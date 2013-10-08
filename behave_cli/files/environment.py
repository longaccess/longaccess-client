from . import setup, teardown
from .file import filename_vars, dirname_vars


def before_all(context):
    setup(context)
    if not hasattr(context, 'format_vars'):
        context.format_vars = []
    context.format_vars.append(filename_vars)
    context.format_vars.append(dirname_vars)


def after_all(context):
    teardown(context)


def before_feature(context, feature):
    pass


def after_feature(context, feature):
    pass


def before_scenario(context, scenario):
    setup(context)


def after_scenario(context, scenario):
    teardown(context)
