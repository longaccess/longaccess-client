import os
from lacli.progress import make_progress, save_progress
from itertools import repeat, izip
from lacli.log import getLogger
from lacli.source.chunked import ChunkedFile
from lacli.exceptions import (UploadEmptyError, WorkerFailureError, PauseEvent,
                              CloudProviderUploadError)
from lacli.control import readControl
from tempfile import mkdtemp
from multiprocessing import active_children


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
        try:
            self.upload = self._getupload()
        except Exception as e:
            raise CloudProviderUploadError(e)
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
        return type is None

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
                    getLogger().debug("got key {} with etag: {}".format(
                        key.name, key.etag))
                    etags.append(key.etag)
            except StopIteration:
                pass
            except WorkerFailureError:
                getLogger().debug("error getting result.", exc_info=True)

        if not etags:
            raise UploadEmptyError()

        if hasattr(self.upload, 'complete_upload'):
            key = self.complete_multipart(etags)
            name = key.key_name
        else:
            name = key.name

        uploaded = len(etags)
        total = self.source.chunks
        getLogger().debug("Uploaded {} out of {} chunks".format(
            uploaded, total))
        size = self.source.size
        if uploaded < total:
            for seq in xrange(uploaded, total):
                make_progress({'part': seq, 'tx': 0})
            skip = self.source.chunkstart(uploaded)
            newsource = ChunkedFile(
                self.source.path, skip=skip, chunk=self.source.chunk)
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
# vim: et:sw=4:ts=4
