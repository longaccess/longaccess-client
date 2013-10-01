from behave import step


@step(u'I have 1 capsule')
def one_capsule(context):
    context.mock_api.test('oneCapsule')
