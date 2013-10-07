from behave_cli import environment as clienv


def before_all(context):
    clienv.before_all(context)


def after_all(context):
    clienv.after_all(context)


def before_feature(context, feature):
    clienv.before_feature(context, feature)


def after_feature(context, feature):
    clienv.after_feature(context, feature)


def before_scenario(context, scenario):
    clienv.before_scenario(context, scenario)
    context.archive = None


def after_scenario(context, scenario):
    clienv.after_scenario(context, scenario)
    if context.archive is not None:
        context.archive.close()
