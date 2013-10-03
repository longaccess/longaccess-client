def api_vars(ctx):
    vs = {}
    if ctx.mock_api is not None:
        vs['api_url'] = ctx.mock_api.url()
    return vs


def setup(context):
    context.mock_api = None


def teardown(context):
    if context.mock_api is not None:
        context.mock_api.close()
    context.mock_api = None
