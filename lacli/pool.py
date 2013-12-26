from __future__ import division
import os
import math
from lacli.date import parse_timestamp, remaining_time
from lacli.progress import make_progress, save_progress
from itertools import imap, repeat, izip
from lacli.log import getLogger
from lacli.exceptions import UploadEmptyError, WorkerFailureError, PauseEvent
from lacli.control import readControl
from boto import connect_s3
from boto.utils import compute_md5
from boto.s3.key import Key
from filechunkio import FileChunkIO
from sys import maxint
from tempfile import mkdtemp, mkstemp
from multiprocessing import TimeoutError, active_children


class MPConnection(object):
    def __init__(self, token, grace=1200):
        self.accesskey = token['token_access_key']
        self.secret = token['token_secret_key']
        self.sectoken = token['token_session']
        self.expiration = token['token_expiration']
        self.uid = token['token_uid']
        self.bucket = token['bucket']
        self.grace = grace
        self.conn = None
        self.expiration = None
        if token.get('token_expiration', None):
            try:
                self.expiration = parse_timestamp(
                    token['token_expiration'])
            except ValueError:
                getLogger().debug("invalid token expiration: %s",
                                  token['token_expiration'])
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

    def newkey(self, key):
        return Key(self.getconnection().get_bucket(self.bucket), key)

    def timeout(self):
        """ return total number of seconds till
            this connection must be renewed. """
        if not self.expiration:
            return None
        remaining = remaining_time(self.expiration)
        return remaining.total_seconds() - self.grace

    def __getstate__(self):
        state = self.__dict__
        state['conn'] = None
        return state


class MPFile(object):
    minchunk = 5242880
    maxchunk = 104857600

    def __init__(self, path, skip=0):
        self.path = path
        self.isfile = os.path.isfile(path)
        size = maxint
        if self.isfile:
            size = os.path.getsize(path)
        assert size >= skip
        self.skip = skip
        self.size = size-skip
        self.chunk = min(max(int(self.size/100), self.minchunk), self.maxchunk)
        self.chunks = int(math.ceil(self.size/self.chunk))
        if self.chunks == 0:
            self.chunks = 1

    def _savedchunks(self, tempdir):
        # split file and save parts to disk
        f = open(self.path, "rb")

        def _save(seq):
            b = f.read(self.chunk)
            if b:
                prefix = "part-{:>4}".format(seq)
                fh, fn = mkstemp(dir=tempdir, prefix=prefix)
                os.write(fh, b)
                os.close(fh)
                return fn
            f.close()

        return imap(_save, xrange(self.chunks))

    def chunkstart(self, num):
        return self.skip + num * self.chunk

    def chunksize(self, num):
        start = num * self.chunk
        if (start + self.chunk > self.size):
            # chunk end is EOF
            return self.size - start
        else:
            return self.chunk

    def chunkfile(self, seq, fname):
        if self.isfile:
            return FilePart(self, seq)
        else:
            return SavedPart(self, seq, fname)


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


class SavedPart(file):
    def __init__(self, source, num, *args, **kwargs):
        super(SavedPart, self).__init__(*args, **kwargs)
        self.bytes = source.chunksize(num)

    hash = FileHash()


class FilePart(FileChunkIO):

    def __init__(self, source, num, *args, **kwargs):
        super(FilePart, self).__init__(
            source.path, 'r',
            offset=source.chunkstart(num),
            bytes=source.chunksize(num), *args, **kwargs)

    hash = FileHash()


class MPUpload(object):

    def __init__(self, connection, source, key, step=None, retries=4):
        self.connection = connection
        self.source = source
        self.retries = retries
        self.key = key
        self.upload_id = None
        self.complete = None
        self.tempdir = None
        self.bucket = None
        self.step = step

    def __str__(self):
        return "<MPUpload key={} id={} source={}>".format(
            self.key, self.upload_id, self.source)

    def iterargs(self, chunks):
        partinfo = repeat(None)
        if not self.source.isfile:
            partinfo = self.source._savedchunks(self.tempdir)
        for seq, info in izip(xrange(chunks), partinfo):
            yield {'uploader': self, 'seq': seq, 'fname': info}

    def _getupload(self):
        if self.bucket is None:
            self.bucket = self.connection.getbucket()

        if self.source.chunks > 1 and self.source.isfile:
            if self.upload_id is None:
                return self.bucket.initiate_multipart_upload(self.key)

            for upload in self.bucket.get_all_multipart_uploads():
                if self.upload_id == upload.id:
                    return upload
        else:
            return self.connection.newkey(self.key)

    def __enter__(self):
        self.upload = self._getupload()
        if not hasattr(self.upload, 'set_contents_from_file'):
            self.upload_id = self.upload.id
            getLogger().debug("multipart upload with id: %s", self.upload_id)
        if not self.source.isfile:
            self.tempdir = mkdtemp()
        return self

    def __exit__(self, type, value, traceback):
        if value is not None:
            getLogger().debug("cancelling upload..", exc_info=True)
            if hasattr(self.upload, 'cancel_upload'):
                self.upload.cancel_upload()
        if self.tempdir is not None:
            os.rmdir(self.tempdir)

    def submit_job(self, pool):
        getLogger().debug("total of %d upload jobs for workers..",
                          self.source.chunks)
        chunks = self.source.chunks
        step = self.step
        if step is None:
            step = len(active_children()) or 5
        if chunks > step:
            chunks = step    
        return pool.imap(upload_part, self.iterargs(chunks))

    def complete_multipart(self, etags):
        xml = '<CompleteMultipartUpload>\n'
        for seq, etag in enumerate(etags):
            xml += '  <Part>\n'
            xml += '    <PartNumber>{}</PartNumber>\n'.format(seq+1)
            xml += '    <ETag>{}</ETag>\n'.format(etag)
            xml += '  </Part>\n'
        xml += '</CompleteMultipartUpload>'
        return self.bucket.complete_multipart_upload(
            self.upload.key_name, self.upload.id, xml)

    def get_result(self, rs):
        etags = []
        key = name = None
        newsource = None
        if rs is not None:
            try:
                while True:
                    key = rs.next(self.connection.timeout())
                    getLogger().debug("got key {} with etag: {}".format(key.name, key.etag))
                    etags.append(key.etag)
            except PauseEvent:
                raise
            except StopIteration:
                pass
            except WorkerFailureError:
                getLogger().debug("error getting result.", exc_info=True)
            except TimeoutError:
                getLogger().debug("stopping before credentials expire.")

        if not etags:
            raise UploadEmptyError()

        if hasattr(self.upload, 'complete_upload'):
            key = self.complete_multipart(etags)
            name = key.key_name
        else:
            name = key.name

        uploaded = len(etags)
        total = self.source.chunks
        getLogger().debug("Uploaded {} out of {} chunks".format(uploaded, total))
        size = self.source.size
        if uploaded < total:
            for seq in xrange(uploaded, total):
                make_progress({'part': seq, 'tx': 0})
            skip = self.source.chunkstart(uploaded)
            newsource = MPFile(self.source.path, skip)
            size = size - newsource.size
        getLogger().debug("saving progress for {}".format(key))
        save_progress(name, size)
        return (key.etag, newsource)

    def do_part(self, seq, **kwargs):
        """ transfer a part. runs in a separate process. """

        key = None
        for attempt in range(self.retries):
            getLogger().debug("attempt %d/%d to transfer part %d",
                              attempt, self.retries, seq)

            with self.source.chunkfile(seq, **kwargs) as part:
                try:
                    def cb(tx, total):
                        readControl()
                        make_progress({'part': seq,
                                       'tx': tx,
                                       'total': total})

                    if hasattr(self.upload, 'upload_part_from_file'):
                        key = self.upload.upload_part_from_file(
                            fp=part,
                            part_num=seq+1,
                            cb=cb,
                            num_cb=100,
                            size=self.source.chunksize(seq),
                            # although not necessary, boto does it,
                            # good to know how:
                            md5=part.hash
                        )
                        getLogger().debug("uploaded multi part key %s/%d",
                                          key, seq+1)
                    else:
                        self.upload.set_contents_from_file(
                            fp=part,
                            cb=cb,
                            num_cb=100,
                            md5=part.hash
                        )
                        key = self.upload
                        getLogger().debug("uploaded single part key %s", key)
                except PauseEvent:
                    raise    
                except Exception as exc:
                    getLogger().debug("exception while uploading part %d",
                                      seq, exc_info=True)

                    if attempt == self.retries-1:
                        raise exc
                else:
                    getLogger().debug("succesfully uploaded %s part %d: %s",
                                      self.source, seq, key)
                    return key


def upload_part(kwargs):
    try:
        seq = kwargs.pop('seq')
        uploader = kwargs.pop('uploader')
        return uploader.do_part(seq, **kwargs)
    except PauseEvent:
        raise
    except Exception as e:
        raise WorkerFailureError(e)
