from behave import step
from boto import connect_s3


@step(u'an S3 bucket named "{name}"')
def s3bucket_named(context, name):
    boto = connect_s3()
    boto.create_bucket(name)
