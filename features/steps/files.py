from behave import step


@step(u'an empty file "foo"')
def empty_file(context):
        assert False
