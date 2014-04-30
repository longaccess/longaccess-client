from lacli.exceptions import PauseEvent
from lacli.pool import MPUpload
from lacore.source.chunked import ChunkedFile
from lacore.storage.s3 import MPConnection
from lacore.api import UploadState as BaseUploadState
from contextlib import contextmanager
from lacli.log import getLogger
from lacli.progress import queueHandler
from lacli.control import ControlHandler
from lacli.worker import WorkerPool
from lacore.async import block
from twisted.internet import defer, threads
from itertools import count
from multiprocessing import TimeoutError
from multiprocessing import get_logger as mp_logging_init
import errno
import signal


class LogHandler(queueHandler):
    def __init__(self, logger='lacli'):
        self.logger = getLogger(logger)

    def handle(self, msg):
        self.logger.handle(msg)


class UploadState(BaseUploadState):
    states = None

    @classmethod
    def has_state(cls, fname):
        if cls.states is None:
            cls.setup()
        if fname in cls.states:
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
    def get(cls, fname, size=None, capsule=None, sandbox=False):
        if cls.states is None:
            cls.setup()
        if fname in cls.states:
            state = cls.states[fname]
            msg = "Can't change {} for upload"
            if size is not None:
                assert state.size == size, msg.format('size')
                cls.states[fname].size = size
            if capsule is not None:
                assert state.capsule.id == capsule.id, msg.format('capsule')
                cls.states[fname].capsule = capsule
            if sandbox is True:
                assert state.sandbox == sandbox, msg.format('sandbox status')
                cls.states[fname].sandbox = True
            return cls.states[fname]
        cls.states[fname] = UploadState(fname, size, capsule=capsule,
                                        sandbox=sandbox)
        return cls.states[fname]

    @classmethod
    def reset(cls, fname):
        if cls.states is None:
            cls.setup()
        if fname not in cls.states:
            raise ValueError("Upload doesn't exist!")
        cls.cache._del_upload(fname)
        return cls.states.pop(fname)

    def __init__(self, archive, size, keys=[],
                 exc=None, paused=True, **kwargs):
        super(UploadState, self).__init__(archive, size, **kwargs)
        self.cache = type(self).cache
        self.logfile = self.control = None
        self.keys = keys
        self.progress = reduce(lambda x, y: x + y['size'], self.keys, 0)
        self.pausing = False
        self._paused = paused
        self.exc = exc
        self.deferred_upload = None

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
        if self._paused is True:
            self._paused = False
            self.cache._write_upload(
                self.uri, self.capsule, self.logfile,
                self.exc, self._paused)
        return self

    @block
    @defer.inlineCallbacks
    def wait_for_upload(self):
        try:
            result = yield self.deferred_upload
            defer.returnValue(result)
        except PauseEvent:
            pass
        if self.pausing is True:
            self.paused()

    def __exit__(self, type, value, traceback):
        if type is not None:
            if type == PauseEvent:
                getLogger().debug("upload paused.")
                self.paused()
            else:
                getLogger().debug("error in upload", exc_info=True)
                self.error(value)
        if self.logfile is not None:
            self.logfile.close()
        self.logfile = self.control = None
        return type is None

    def keydone(self, key, size):
        assert self.logfile is not None, "Log not open"
        self.keys.append(
            self.cache._checkpoint_upload(key, size, self.logfile))

    def update(self, progress):
        self.progress = progress

    @property
    def seq(self):
        return len(self.keys)

    def pause(self):
        if not self.pausing and self.control is not None:
            self.control.pause()
        self.pausing = True

    def paused(self):
        getLogger().debug("upload state paused")
        if self.exc is not None:
            getLogger().debug("can't pause a failed upload")
            return
        self._paused = True
        if self.pausing is True:
            self.pausing = False
        self.cache._write_upload(
            self.uri, self.capsule, self.logfile,
            self.exc, self._paused)

    def active(self):
        return self._paused is False and self.exc is None

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
        self.cache._write_upload(op.uri, self.capsule, self.logfile,
                                 self.exc, self._paused)
        self.uri = op.uri

    def error(self, exc):
        if self.exc is None:
            self.cache._write_upload(self.uri, self.capsule,
                                     self.logfile, str(exc), self._paused)
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
                mp_logging_init()
                pool = WorkerPool(
                    self.prefs, logq, progq, ctrlq)
                try:
                    yield pool
                finally:
                    getLogger().debug("terminating pool")
                    pool.terminate()
                    pool.join()

    def upload_temp(self, token, source, etags, pool, seq):
        key = "temp-archive-{seq}".format(seq=seq)
        connection = MPConnection(**token)
        with MPUpload(connection, source, key) as uploader:
            etags[key], source = uploader.get_result(
                uploader.submit_job(pool))
        return source

    @defer.inlineCallbacks
    def upload(self, fname, upload, progq):
        with self._workers(progq) as pool:
            etags = {}
            source = ChunkedFile(fname, self.state.progress)

            token = yield upload.status

            for seq in count(start=self.state.seq):
                try:
                    source = yield threads.deferToThread(
                        self.upload_temp, token, source, etags, pool, seq)
                except PauseEvent:
                    getLogger().debug(
                        "paused after uploading %d temporary keys", seq)
                    raise
                except TimeoutError:
                    getLogger().debug(
                        "timeout after uploading %d temporary keys", seq)
                    token = yield upload.status
                if source is None:
                    getLogger().debug("uploaded entire archive")
                    break

            getLogger().debug("uploaded %d temp keys", len(etags))
            for key, tag in etags.iteritems():
                getLogger().debug("key: %s (etag: %s)", key, tag)
# vim: et:sw=4:ts=4
