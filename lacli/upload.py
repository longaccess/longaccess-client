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
        self.session = session
        self.prefs = prefs

    def upload(self, fname, logq, progq):
        try:
            initargs = (logq, progq)
            nprocs = self.prefs['nprocs']
            pool = mp.Pool((nprocs or max(mp.cpu_count()-1, 1)),
                           initworker, initargs)
            source = lacli.pool.File(fname)
            keys = []
            seq = 1
            for token in self.session.tokens():
                name = "archive-{}".format(seq)
                conn = lacli.pool.MPConnection(token)
                try:
                    res = upload_temp_key(pool.imap, source, conn, name=name)
                    keys.append((res[0], res[1]))
                    if res[2] is None:
                        break
                    source = res[2]  # continue with remaining file
                    seq += 1
                except Exception:
                    getLogger().debug("couldn't upload to temporary key",
                                      exc_info=True)
                    raise
            getLogger().debug("uploaded %d temp keys", len(keys))
            for key in keys:
                getLogger().debug("key: %s (etag: %s)", key[0], key[1])
            # TODO join keys into one key
        except Exception:
            getLogger().debug("exception", exc_info=True)
            raise
        finally:
            getLogger().debug("terminating all procs..")
            pool.terminate()
