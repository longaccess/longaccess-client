from __future__ import division
import os
import dateutil.parser
import dateutil.tz
import datetime
import math
from lacli.log import getLogger
from boto import connect_s3
from boto.utils import compute_md5
from filechunkio import FileChunkIO


class Progress(object):
    def __init__(self):
        self.queue = None


progress = Progress()


class MPConnection(object):
    def __init__(self, token, bucket='lastage', grace=1200):
        self.accesskey = token['token_access_key']
        self.secret = token['token_secret_key']
        self.sectoken = token['token_session']
        self.expiration = token['token_expiration']
        self.uid = token['token_uid']
        self.bucket = bucket
        self.grace = grace
        self.conn = None
        if self.uid is None:
            self.uid = self.getconnection().get_canonical_user_id()

    def getconnection(self):
        if self.conn is None:
            self.conn = connect_s3(
                aws_access_key_id=self.accesskey,
                aws_secret_access_key=self.secret,
                security_token=self.sectoken)
        return self.conn

    def getbucket(self):
        return self.getconnection().get_bucket(self.bucket)

    def timeout(self):
        """ return total number of seconds till
            this connection must be renewed. """
        tz = dateutil.tz.tzutc()
        expiration = dateutil.parser.parse(self.expiration).astimezone(tz)
        timeout = expiration-datetime.datetime.now(tz)
        return timeout.total_seconds()-self.grace

    def __getstate__(self):
        state = self.__dict__
        state['conn'] = None
        return state


class File(object):
    minchunk = 5242880

    def __init__(self, path, skip=0):
        self.path = path
        self.skip = 0
        self.size = os.path.getsize(self.path)-self.skip
        self.chunk = max(int(self.size/100), self.minchunk)
        self.chunks = int(math.ceil(self.size/self.chunk))
        if self.chunks == 0:
            self.chunks = 1

    def chunkstart(self, num):
        return self.skip + num * self.chunk

    def chunksize(self, num):
        start = self.chunkstart(num)
        if (start + self.chunk > self.size):
            # chunk end is EOF
            return self.size - start
        else:
            return self.chunk


class FileHash(object):
    def __get__(self, instance, owner):
        try:
            return (instance.md5, instance.b64md5)
        except AttributeError:
            instance.seek(0)
            (instance.md5, instance.b64md5, size) = compute_md5(
                instance, instance.bytes)
            instance.seek(0)
            return (instance.md5, instance.b64md5)


class FilePart(FileChunkIO):

    def __init__(self, source, num, *args, **kwargs):
        super(FilePart, self).__init__(
            source.path, 'r',
            offset=source.chunkstart(num),
            bytes=source.chunksize(num), *args, **kwargs)

    hash = FileHash()


class UploadError(Exception):
    pass


class PartUploadError(UploadError):
    def __init__(self, msg="", part=None, *args, **kwargs):
        super(PartUploadError, self).__init__(
            msg, *args, **kwargs)
        self.part = part


class UploadEmptyError(UploadError):
    pass


class MPUpload(object):

    def __init__(self, connection, source,
                 name="archive", prefix="upload", retries=4):
        self.connection = connection
        self.source = source
        self.retries = retries
        self.name = name
        self.folder = "{prefix}/{uid}".format(prefix=prefix,
                                              uid=self.connection.uid)
        self.key = "{folder}/temp-{name}".format(folder=self.folder, name=name)
        self.upload_id = None
        self.results = []
        self.complete = None

    def __str__(self):
        return "<MPUload key={} id={} source={}>".format(
            self.key, self.upload_id, self.source)

    def _getupload(self):
        bucket = self.connection.getbucket()

        if self.upload_id is None:
            return bucket.initiate_multipart_upload(self.key)

        for upload in bucket.get_all_multipart_uploads():
            if self.upload_id == upload.id:
                return upload

    def __enter__(self):
        self.upload = self._getupload()
        self.upload_id = self.upload.id
        getLogger().debug("processing upload with id: %s", self.upload_id)
        return self

    def __exit__(self, type, value, traceback):
        if len(self.results) == 0:
            self.upload.cancel_upload()
        # set key acl

    def combineparts(self, successfull):
        if len(successfull) > 0:
            result = self.upload.complete_upload()
            source = None
            if len(successfull) < self.source.chunks:
                source = File(self.source.path,
                              self.source.chunkstart(len(successfull)))

            return (result.key_name, result.etag, source)
        else:
            raise UploadEmptyError()

    def do_part(self, seq):
        """ transfer a part. runs in a separate process. """
        # reestablish the connection
        for attempt in range(self.retries):
            getLogger().debug("attempt %d/%d to transfer part %d",
                              attempt, self.retries, seq)

            with FilePart(self.source, seq) as part:
                try:
                    def cb(tx, total):
                        # fetch progress queue from global scope
                        progress.queue.put({'part': seq,
                                            'tx': tx,
                                            'total': total})
                    self.upload.upload_part_from_file(
                        fp=part,
                        part_num=seq+1,
                        cb=cb,
                        num_cb=100,
                        size=part.bytes,
                        # although not necessary, boto does it,
                        # good to know how:
                        md5=part.hash,
                    )
                except Exception as exc:
                    getLogger().debug("exception while uploading part %d",
                                      seq, exc_info=True)

                    if attempt == self.retries-1:
                        raise exc
                else:
                    getLogger().debug("succesfully uploaded %s part %d",
                                      self.source, seq)
                    return seq


def upload_part(args):
    try:
        chunk = args[0]
        upload = args[1]
        getLogger().debug("uploading chunk %d", chunk)
        upload.do_part(chunk)
    except Exception:
        getLogger().debug("exception uploading chunk %d",
                          args[0], exc_info=True)
        pass
