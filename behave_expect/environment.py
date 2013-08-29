from . import setup, teardown


def before_all(context):
    setup(context)


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
