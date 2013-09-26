from moto import mock_s3


def setup(context):
    context.moto = mock_s3()
    context.moto.start()


def teardown(context):
    context.moto.stop()
