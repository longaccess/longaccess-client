from behave import step
from boto import connect_s3
from boto import config as boto_config


@step(u'an S3 bucket named "{name}"')
def s3bucket_named(context, name):
    if not boto_config.has_section('Boto'):
        boto_config.add_section('Boto')
    boto_config.set('Boto', 'debug', '0')
    boto = connect_s3()
    boto.create_bucket(name)
    context.buckets.append(name)
