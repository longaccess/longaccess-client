import os


def before_all(context):
    context.environ = os.environ.copy()


def after_all(context):
    pass


def before_feature(context, feature):
    pass


def after_feature(context, feature):
    pass


def before_scenario(context, scenario):
    pass


def after_scenario(context, scenario):
    pass
