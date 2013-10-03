from lacli.pool import MPConnection, MPUpload, MPFile
from contextlib import contextmanager
from lacli.log import LogHandler, getLogger
from lacli.progress import ProgressHandler
from lacli.worker import WorkerPool
from multiprocessing import cpu_count, Pool


class Upload(object):
    def __init__(self, session, prefs):
        self.tokens = session.tokens()
        self.prefs = prefs
        self.log = LogHandler()
        self.prefix = 'upload'

    @contextmanager
    def _workers(self, progq):
        with self.log as logq:
            pool = WorkerPool(self.prefs, logq, progq)
            yield pool
            pool.terminate()

    def upload(self, fname):
        with ProgressHandler(fname) as progq:
            with self._workers(progq) as pool:
                etags = {}
                source = MPFile(fname)
                for token, key in self._nexttoken():
                    connection = MPConnection(token)
                    with MPUpload(connection, source, key) as uploader:
                        etags[key], source = uploader.get_result(
                            uploader.submit_job(pool))
                        if source is None:
                            break
                getLogger().debug("uploaded %d temp keys", len(etags))
                for key, tag in etags.iteritems():
                    getLogger().debug("key: %s (etag: %s)", key, tag)

    def _nexttoken(self):
        for seq, token in enumerate(self.tokens):
            yield token, "{prefix}/{uid}/temp-archive-{seq}".format(
                prefix=self.prefix,
                uid=token['token_uid'],
                seq=seq)
