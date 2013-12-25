from lacli.exceptions import PauseEvent
from lacli.pool import MPConnection, MPUpload, MPFile
from contextlib import contextmanager
from lacli.log import LogHandler, getLogger
from lacli.control import ControlHandler
from lacli.worker import WorkerPool
from twisted.internet import defer, threads
from itertools import count
import json
import errno
import signal


class UploadState(object):
    states = {}
    
    
    @classmethod
    def init(cls, cache):
        cls.cache = cache
        uploads = cache._get_uploads()
        a = cache._for_adf('archives')
        sz = lambda f: a[f]['archive'].meta.size
        cls.states = {k: cls(k, sz(k), v[1], v[0])
            for k, v in uploads.iteritems()}

    @classmethod
    def get(cls, fname, size):
        if fname in cls.states:
            return cls.states[fname]
        return UploadState(fname, size)
    
    def __init__(self, archive, size, keys=[], uri=None):
        self.cache = type(self).cache
        self.archive = archive
        self.logfile = self.control = None
        self.keys = keys
        self._progress = 0
        self.size = size
        self.pausing = False
        self.uri = uri

    def append(self, key):
        self.keys.append(key)

    @property
    def progress(self):
        f = lambda x, y: x + y['size']
        return self._progress + reduce(f, self.keys, 0)

    def __enter__(self):
        try:
            self.control = ControlHandler()
            self.logfile = self.cache._upload_open(self.archive, mode='r+')
            getLogger().debug("Found state file for %s", self.archive)
        except IOError as e:
            if e.errno == errno.ENOENT:
                getLogger().debug("Creating state file for %s", self.archive)
                self.logfile = self.cache._upload_open(self.archive, mode='w+')
            else:
                raise e
        # update keys from file
        self.uri, self.keys = self.cache._validate_upload(self.logfile)
        return self

    def __exit__(self, type, value, traceback):
        self.logfile.close()
        self.logfile = self._progress = self.control = None

    def keydone(self, key, size):
        assert self.logfile is not None, "Log not open"
        new = { 'name': key, 'size': size}
        self.logfile.write(json.dumps(new)+"\n")
        self.logfile.flush()
        self.append(new)
        self._progress = 0

    def update(self, progress):
        self._progress += progress

    @property
    def seq(self):
        return len(self.keys)

    def pause(self):
        self.control.pause()

    def signal(self, sig, frame):
        getLogger().debug("Got interrupt")
        if sig == signal.SIGINT:
            getLogger().debug("Pausing")
            if self.pausing is True:
                raise SystemExit("Interrupted")
            self.pausing = True
            self.control.pause()
            
    def save_op(self, op):
        assert self.uri is None, "Can't change URI for upload state"
        if op.uri is None:
            return
        new = { 'uri': op.uri }
        self.logfile.write(json.dumps(new)+"\n")
        self.logfile.flush()
        self.uri = op.uri


class Upload(object):
    def __init__(self, session, nprocs, debug, state):
        self.prefs = {
            'nprocs': nprocs,
            'debugworker': debug > 2
        }
        self.log = LogHandler()
        self.state = state

    @contextmanager
    def _workers(self, progq):
        with self.log as logq:
            with self.state.control as ctrlq:
                pool = WorkerPool(
                    self.prefs, logq, progq, ctrlq)
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
            source = MPFile(fname, self.state.progress)

            for seq in count(start=self.state.seq):
                token = yield upload.status
                try:
                    source = yield threads.deferToThread(
                        self.upload_temp, token, source, etags, pool, seq)
                except PauseEvent:
                    getLogger().debug("paused after uploading %d temp keys",
                        len(etags))
                    break
                if source is None:
                    progq.put({'complete': True})
                    break

            getLogger().debug("uploaded %d temp keys", len(etags))
            for key, tag in etags.iteritems():
                getLogger().debug("key: %s (etag: %s)", key, tag)
