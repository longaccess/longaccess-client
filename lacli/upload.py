import lacli.pool
import multiprocessing as mp
from itertools import repeat
from lacli.log import getLogger, logToQueue


def results(it, timeout):
    while True:
        yield it.next(timeout)


def upload_temp_key(poolmap, source, conn, name='archive'):
    with lacli.pool.MPUpload(conn, source, name=name) as upload:
        getLogger().debug("sending %d upload jobs to workers..",
                          source.chunks)
        args = enumerate(repeat(upload, source.chunks))
        rs = poolmap(lacli.pool.upload_part, args)
        successfull = []
        try:
            for r in results(rs, conn.timeout()):
                successfull.append(r)
        except StopIteration:
            pass
        except mp.TimeoutError:
            getLogger().debug("stopping before credentials expire.")
        return upload.combineparts(successfull)


def initworker(logq, progq):
    """initializer that sets up logging and progress from sub procs """
    logToQueue(logq)
    lacli.pool.progress.queue = progq


class Upload(object):
    def __init__(self, session, prefs):
        self.tokens = session.tokens()
        self.prefs = prefs

    def upload(self, fname, logq, progq):
        try:
            initargs = (logq, progq)
            nprocs = self.prefs['nprocs']
            pool = mp.Pool((nprocs or max(mp.cpu_count()-1, 1)),
                           initworker, initargs)
            source = lacli.pool.File(fname)
            etags = {}
            seq = 1
            while source is not None:
                name = "archive-{}".format(seq)
                conn = lacli.pool.MPConnection(next(self.tokens))
                try:
                    key, etags[key], source = upload_temp_key(
                        pool.imap, source, conn, name=name)
                    seq += 1
                except Exception:
                    getLogger().debug("couldn't upload to temporary key",
                                      exc_info=True)
                    raise
            getLogger().debug("uploaded %d temp keys", len(etags))
            for key, etag in etags.iteritems():
                getLogger().debug("key: %s (etag: %s)", key, etag)
            # TODO join keys into one key
        except Exception:
            getLogger().debug("exception", exc_info=True)
            raise
        finally:
            getLogger().debug("terminating all procs..")
            pool.terminate()
