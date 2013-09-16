import lacli.pool
import multiprocessing as mp
from itertools import repeat
from lacli.log import getLogger, logToQueue
from lacli.exceptions import ApiUnavailableException, ApiErrorException


class UploadManager(object):

    def __init__(self, session):
        self.session = session

    def __enter__(self, **kwargs):
        return Upload(self.session.tokens,
                      poolsize=self.session.nprocs, **kwargs)

    def __exit__(self, type, value, tb):
        if type is not None:
            return self._handle_error(type)

    def _handle_error(self, type):
        if type is ApiUnavailableException:
            print "error: server not found"
        elif type is ApiErrorException:
            print "error: the server couldn't fulfill your request"
        else:
            print "error: unknown"
        getLogger().debug("exception while uploading",
                          exc_info=True)
        return True


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
    def __init__(self, tvm, poolsize=None):
        self.tvm = tvm
        self.poolsize = poolsize
        if self.poolsize is None:
            self.poolsize = max(mp.cpu_count()-1, 1)

    def upload(self, fname, param={}):
        try:
            pool = mp.Pool(self.poolsize, initworker, param)
            source = lacli.pool.File(fname)
            keys = []
            seq = 1
            for token in self.tvm():
                name = "archive-{}".format(seq)
                conn = lacli.pool.MPConnection(token)
                try:
                    res = upload_temp_key(pool.imap, source, conn, name=name)
                    keys.append((res[0], res[1]))
                    if res[2] is None:
                        break
                    source = res[2]  # continue with remaining file
                except Exception:
                    getLogger().error("couldn't upload to temporary key",
                                      exc_info=True)
                    break
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
