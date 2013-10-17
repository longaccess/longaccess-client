from lacli.pool import MPConnection, MPUpload, MPFile
from contextlib import contextmanager
from lacli.log import LogHandler, getLogger
from lacli.progress import ProgressHandler
from lacli.worker import WorkerPool


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

    def upload(self, fname, tokens):
        with ProgressHandler(fname) as progq:
            with self._workers(progq) as pool:
                etags = {}
                source = MPFile(fname)
                for token, key in self._nexttoken(tokens):
                    connection = MPConnection(token)
                    with MPUpload(connection, source, key) as uploader:
                        etags[key], source = uploader.get_result(
                            uploader.submit_job(pool))
                        if source is None:
                            progq.put({'complete': True})
                            break
                getLogger().debug("uploaded %d temp keys", len(etags))
                for key, tag in etags.iteritems():
                    getLogger().debug("key: %s (etag: %s)", key, tag)

    def _nexttoken(self, tokens):
        for seq, token in enumerate(tokens):
            yield token, "{prefix}temp-archive-{seq}".format(
                prefix=token['prefix'],
                seq=seq)
