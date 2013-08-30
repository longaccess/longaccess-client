from behave_expect import environment as benv
import logging


def before_all(context):
    benv.before_all(context)
    if not context.config.log_capture:
        logging.basicConfig(level=logging.DEBUG)
    context.file = None
    context.files = {}


def after_all(context):
    benv.after_all(context)


def before_feature(context, feature):
    benv.before_feature(context, feature)


def after_feature(context, feature):
    benv.after_feature(context, feature)


def before_scenario(context, scenario):
    benv.before_scenario(context, scenario)
    context.file = None
    context.files = {}


def after_scenario(context, scenario):
    benv.after_scenario(context, scenario)
