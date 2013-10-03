def setup(context):
    context.username = None
    context.password = None


def teardown(context):
    pass


def netrc_vars(ctx):
    return {'username': ctx.username, 'password': ctx.password}
