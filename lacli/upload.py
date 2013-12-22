from lacli.pool import MPConnection, MPUpload, MPFile
from contextlib import contextmanager
from lacli.log import LogHandler, getLogger
from lacli.worker import WorkerPool
from twisted.internet import defer, threads
from itertools import count


class Upload(object):
    def __init__(self, session, nprocs, debug):
        self.prefs = {
            'nprocs': nprocs,
            'debugworker': debug > 2
        }
        self.log = LogHandler()

    @contextmanager
    def _workers(self, progq):
        with self.log as logq:
            pool = WorkerPool(self.prefs, logq, progq)
            yield pool
            pool.terminate()

    def upload_temp(self, token, source, etags, pool, seq):
        key = "{prefix}temp-archive-{seq}".format(
            prefix=token['prefix'], seq=seq)
        connection = MPConnection(token)
        with MPUpload(connection, source, key) as uploader:
            etags[key], source = uploader.get_result(
                uploader.submit_job(pool))
        return source

    @defer.inlineCallbacks
    def upload(self, fname, upload, progq):
        with self._workers(progq) as pool:
            etags = {}
            source = MPFile(fname)

            for seq in count():
                token = yield upload.status
                source = yield threads.deferToThread(
                    self.upload_temp, token, source, etags, pool, seq)
                if source is None:
                    progq.put({'complete': True})
                    break

            getLogger().debug("uploaded %d temp keys", len(etags))
            for key, tag in etags.iteritems():
                getLogger().debug("key: %s (etag: %s)", key, tag)
