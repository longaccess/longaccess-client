from behave_cli.expect import environment as expenv
from behave_cli.files import environment as fileenv


def before_all(context):
    expenv.before_all(context)
    fileenv.before_all(context)


def after_all(context):
    expenv.after_all(context)
    fileenv.after_all(context)


def before_feature(context, feature):
    expenv.before_feature(context, feature)
    fileenv.before_feature(context, feature)


def after_feature(context, feature):
    expenv.after_feature(context, feature)
    fileenv.after_feature(context, feature)


def before_scenario(context, scenario):
    expenv.before_scenario(context, scenario)
    fileenv.before_scenario(context, scenario)


def after_scenario(context, scenario):
    expenv.after_scenario(context, scenario)
    fileenv.after_scenario(context, scenario)
