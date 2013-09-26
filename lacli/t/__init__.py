from boto import set_stream_logger


def setup():
    set_stream_logger('boto')
