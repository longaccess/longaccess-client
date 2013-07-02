from __future__ import division
import os
import sys
import time
import dateutil.parser
import dateutil.tz
import datetime
import random
import math
from boto.s3.connection import S3Connection
from boto.utils import compute_md5
from filechunkio import FileChunkIO


class MPConnection(object):
    def __init__(self, token, bucket='lastage', grace=1200):
        self.accesskey=token[0]
        self.secret=token[1]
        self.sectoken=token[2]
        self.expiration=token[3]
        self.uid=token[4]
        self.bucket=bucket
        self.grace=grace
        self.conn=None
    def getconnection(self):
        if self.conn is None:
            self.conn = S3Connection(self.accesskey, self.secret, security_token=self.sectoken)
        return self.conn
    def getbucket(self):
        return self.getconnection().get_bucket(self.bucket)
    def timeout(self):
        """ return total number of seconds till
            this connection must be renewed. """
        tz=dateutil.tz.tzutc()
        expiration=dateutil.parser.parse(self.expiration).astimezone(tz)
        timeout=expiration-datetime.datetime.now(tz)
        return timeout.total_seconds()-self.grace
    def __getstate__(self):
        state=self.__dict__
        state['conn']=None
        return state

class File(object):
    maxchunk=5242880
    def __init__(self, path, skip=0):
        self.path=path
        self.skip=0
        self.size=os.path.getsize(self.path)-self.skip
        self.chunk=max(int(self.size/100), self.maxchunk)
        self.chunks=int(math.ceil(self.size/self.chunk))
    def chunkstart(self, num):
        return self.skip + num * self.chunk
    def chunksize(self, num):
        start=self.chunkstart(num)
        if (start + self.chunk > self.size):
            # chunk end is EOF
            return self.size - start
        else:
            return self.chunk


class FileHash(object):
    def __get__(self, instance, owner):
        try:
            return (instance.md5,instance.b64md5)
        except AttributeError:
            instance.seek(0)
            (instance.md5,instance.b64md5,size) = compute_md5(instance,instance.bytes)
            print "calculated md5 for offset={0}/size={1}: {2}".format(
                    instance.offset,
                    instance.bytes,
                    instance.b64md5)
            instance.seek(0)
            return (instance.md5,instance.b64md5)

class FilePart(FileChunkIO):

    def __init__(self, source, num, *args, **kwargs):
        super(FilePart, self).__init__(source.path, 'r', 
                offset=source.chunkstart(num), 
                bytes=source.chunksize(num), *args, **kwargs)

    hash=FileHash()


class UploadError(Exception): pass

class PartUploadError(UploadError):
    def __init__(self, msg="", part=None, *args, **kwargs):
        super(PartUploadException, self).__init__(
                msg, *args, **kwargs)
        self.part=part

class UploadEmptyError(UploadError): pass
        
class MPUpload(object):

    def __init__(self, connection, source, name="archive", prefix="upload", retries=4):
        self.connection=connection
        self.source=source
        self.retries=retries
        self.name=name
        self.folder="{prefix}/{uid}".format(prefix=prefix,uid=self.connection.uid)
        self.key="{folder}/temp-{name}".format(folder=self.folder,name=name)
        self.upload_id=None
        self.results=[]
        self.complete=None

    def __str__(self):
        return "<MPUload key={} id={} source={}>".format(self.key, self.upload_id, self.source)
    def _getupload(self):
        bucket=self.connection.getbucket()

        print "trying to initiate upload to {}".format(self.key)
        if self.upload_id is None:
            return bucket.initiate_multipart_upload(self.key)

        print "trying to retrieve previous upload to {0} (id: {1})".format(
                self.key, self.upload_id)
        for upload in bucket.get_all_multipart_uploads():
            if self.upload_id == upload.id:
                return upload 

    def __enter__(self):
        self.upload=self._getupload()
        print "upload id: "+self.upload.id 
        self.upload_id=self.upload.id 
        return self
    def __exit__(self,type, value, traceback):
        if len(self.results) == 0:
            self.upload.cancel_upload()
        # set key acl
    def combineparts(self, successfull):
        if len(successfull) > 0:
            result=self.upload.complete_upload()
            source=None
            if len(successfull)<self.source.chunks:
                source=File(self.source.path, self.source.chunkstart(len(successfull)))

            return (result.key_name, result.etag, source)
        else:
            raise UploadEmptyError()
    def do_part(self, seq):
        """ transfer a part. runs in a separate process. """
        # reestablish the connection
        for attempt in range(self.retries):
            print "attempt {0} to transfer part {1}".format(attempt, seq)

            with FilePart(self.source, seq) as part:
                try:
                    print "chunk {0}, offset {1}, size {2}".format(seq, part.offset, part.bytes)
                    self._upload_part(seq, part)
                except Exception as exc:
                    print 'failed to upload part {0}'.format(seq)
                    import traceback
                    traceback.print_exc()

                    if attempt==self.retries-1:
                        print "giving up on part {0} after {1} tries".format(
                                seq, self.retries)
                        raise exc
                else:
                    print 'succesfully uploaded {0} part {1}'.format(
                        self.source, seq)
                    return seq

    def _upload_part(self, seq, part):
        print "MD5: "+part.hash[1]
        self.upload.upload_part_from_file(
                fp=part,
                part_num=seq+1,
                cb=self._progress(part),
                num_cb=10,
                size=part.bytes,
                # although not necessary, good to know how:
                md5=part.hash,
                )

    def _progress(self, seq):
        def cb(tx, total):
            sys.stdout.write('.')
            sys.stdout.flush()
            if tx == total:
                print "completed part {}".format(seq)
        return cb

def upload_part(args):
    try:
        print "worker uploading chunk {}".format(args[0])
        upload=args[1]
        upload.do_part(args[0])
    except Exception as e:
        import traceback
        traceback.print_exc()
        pass

