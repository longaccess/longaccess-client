from behave import step


@step(u'the home directory is "{dir}"')
def home_directory(context, dir):
    assert False


@step(u'I run "{command}"')
def run_command(context, command):
    assert False


@step(u'I see "{text}"')
def i_see_text(context, text):
    assert False
