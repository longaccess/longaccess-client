from lacli.exceptions import PauseEvent
from lacli.pool import MPConnection, MPUpload, MPFile
from contextlib import contextmanager
from lacli.log import LogHandler, getLogger
from lacli.control import ControlHandler
from lacli.worker import WorkerPool
from twisted.internet import defer, threads
from itertools import count
from multiprocessing import TimeoutError
import json
import errno
import signal


class UploadState(object):
    states = None
    
    @classmethod
    def has_state(cls, fname):
        if cls.states is not None and fname in cls.states:
            return True
        return False
    
    @classmethod
    def init(cls, cache):
        cls.cache = cache

    @classmethod
    def setup(cls):
        uploads = cls.cache._get_uploads()
        a = cls.cache._for_adf('archives')
        sz = lambda f: a[f]['archive'].meta.size
        cls.states = {k: cls(k, sz(k), **v)
            for k, v in uploads.iteritems()
            if k in a}

    @classmethod
    def get(cls, fname, size=None, capsule=None):
        if cls.states is None:
            cls.setup()
        if fname in cls.states:
            if size is not None:
                cls.states[fname].size = size
            if capsule is not None:
                cls.states[fname].capsule = capsule
            return cls.states[fname]
        cls.states[fname] = UploadState(fname, size, capsule=capsule)
        return cls.states[fname]

    @classmethod
    def reset(cls, fname):
        if fname not in cls.states:
            raise ValueError("Upload doesn't exist!")
        cls.cache._del_upload(fname)
        return cls.states.pop(fname)
    
    def __init__(self, archive, size, uri=None, keys=[], capsule=None, exc=None):
        self.cache = type(self).cache
        self.archive = archive
        self.logfile = self.control = None
        self.keys = keys
        self.progress = reduce(lambda x, y: x + y['size'], self.keys, 0)
        self.size = size
        self.pausing = False
        self.uri = uri
        self.exc = exc
        self.capsule = capsule

    def __enter__(self):
        try:
            self.exc = None
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
        upload = self.cache._validate_upload(self.logfile)
        self.uri = upload.get('uri', self.uri)
        self.keys = upload.get('keys', self.keys)
        return self

    def __exit__(self, type, value, traceback):
        if self.logfile is not None:
            self.logfile.close()
        self.logfile = self.control = None
        self.progress = 0

    def keydone(self, key, size):
        assert self.logfile is not None, "Log not open"
        self.keys.append(self.cache._checkpoint_upload(key, size, self.logfile))

    def update(self, progress):
        self.progress = progress

    @property
    def seq(self):
        return len(self.keys)

    def pause(self):
        if self.control is not None:
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
        self.cache._write_upload(op.uri, self.capsule, self.logfile)
        self.uri = op.uri

    def error(self, exc):
        if self.exc is None:
            self.cache._write_upload(self.uri, self.capsule, self.logfile, str(exc))
            self.exc = exc

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
                try: 
                    yield pool
                finally:
                    pool.terminate()
                    pool.join()

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
                    getLogger().debug("paused after uploading %d temporary keys", seq)
                    raise
                except TimeoutError:
                    getLogger().debug("timeout after uploading %d temporary keys", seq)
                if source is None:
                    getLogger().debug("uploaded entire archive")
                    break

            getLogger().debug("uploaded %d temp keys", len(etags))
            for key, tag in etags.iteritems():
                getLogger().debug("key: %s (etag: %s)", key, tag)
