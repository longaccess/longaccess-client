import boto.s3
import boto.s3.connection
from botofun import BOTO_ACCESS_KEY, BOTO_SECRET, BOTO_BUCKET

class Upload(object):
    def __init__(self):
        self.connection = boto.s3.connection.S3Connection(BOTO_ACCESS_KEY, BOTO_SECRET)
