import os
from behave import step
from behave_cli import format_vars


@step(u'the username "{username}"')
def the_username(context, username):
    context.username = username


@step(u'the password "{password}"')
def the_password(context, password):
    context.password = password


@step(u'I store my credentials in "{file}"')
@format_vars
def store_in_netrc(context, file):
    pass
