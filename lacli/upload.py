from lacli.pool import MPConnection, MPUpload, MPFile
from contextlib import contextmanager
from lacli.log import LogHandler, getLogger, logToQueue
from lacli.progress import ProgressHandler, progressToQueue
from multiprocessing import cpu_count, Pool


def initworker(logq, progq):
    """initializer that sets up logging and progress from sub procs """
    logToQueue(logq)
    progressToQueue(progq)


class Upload(object):
    def __init__(self, session, prefs):
        self.tokens = session.tokens()
        self.nprocs = prefs['nprocs'] or max(cpu_count()-1, 1)
        self.log = LogHandler()
        self.prefix = 'upload'

    @contextmanager
    def _workers(self, initargs):
        getLogger().debug("setting up pool of {} procs..".format(self.nprocs))
        pool = Pool(self.nprocs, initworker, initargs)
        yield pool
        getLogger().debug("terminating all procs..")
        pool.terminate()

    def upload(self, fname):
        with self.log as log, ProgressHandler(fname) as prog:
            with self._workers((log, prog)) as pool:
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
