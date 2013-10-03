from behave.log_capture import capture
from . import setup, teardown
from . import api_vars


@capture
def before_all(context):
    setup(context)
    if not hasattr(context, 'format_vars'):
        context.format_vars = []
    context.format_vars.append(api_vars)


@capture
def after_all(context):
    teardown(context)


def before_feature(context, feature):
    pass


def after_feature(context, feature):
    pass


@capture
def before_scenario(context, scenario):
    setup(context)


@capture
def after_scenario(context, scenario):
    teardown(context)
