import os
import multiprocessing
from progressbar import (ProgressBar, Bar,
                         ETA, FileTransferSpeed)
from lacore.log import getLogger
from abc import ABCMeta, abstractmethod
from logutils.queue import QueueListener


class queueHandler(object):
    def __enter__(self):
        q = multiprocessing.Queue()
        self.listener = QueueListener(q, self)
        self.listener.start()
        return q

    def __exit__(self, type, value, traceback):
        self.listener.stop()


class BaseProgressHandler(queueHandler, ProgressBar):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.tx = {}
        self.progress = kwargs.pop('progress', 0)
        super(BaseProgressHandler, self).__init__(*args, **kwargs)

    def update_current(self, msg):
        self.tx[msg['part']] = int(msg['tx'])
        return sum(self.tx.values())

    def save_current(self):
        self.progress += sum(self.tx.values())
        self.tx = {}

    def handle(self, msg):
        if 'part' in msg:
            self.update(self.progress + self.update_current(msg))
        elif 'save' in msg:
            self.keydone(msg)
            self.save_current()

    def __enter__(self):
        q = super(BaseProgressHandler, self).__enter__()
        progressToQueue(q)
        self.start(initval=self.progress)
        return q

    @abstractmethod
    def keydone(self, msg):
        getLogger().debug("saved key: {key} ({size})".format(msg))


class StateProgressHandler(BaseProgressHandler):
    uploads = {}

    def __init__(self, state=None, **kwargs):
        assert state is not None, \
            "StateProgressHandler requires a state object"
        self.state = state
        progress = kwargs.pop('progress', 0)
        for seq, key in enumerate(self.state.keys):
            progress += key['size']
        kwargs['progress'] = progress
        super(StateProgressHandler, self).__init__(**kwargs)

    def update(self, value=None):
        if value is not None:
            self.state.update(value)
        super(StateProgressHandler, self).update(value)
        getLogger().debug("State progress: {}".format(self.state.progress))

    def __enter__(self):
        type(self).uploads[self.state] = self
        return super(StateProgressHandler, self).__enter__()

    def __exit__(self, cls, value, traceback):
        del type(self).uploads[self.state]

    def keydone(self, msg):
        getLogger().debug("saving key " + str(msg['key']) + " to state file")
        self.state.keydone(msg['key'], msg['size'])


class ConsoleProgressHandler(StateProgressHandler):
    def __init__(self, *args, **kwargs):
        fname = kwargs.pop('fname', "-")
        kwargs.setdefault('widgets', [fname, ' : ', Bar(), ' ',
                                      ETA(), ' ', FileTransferSpeed()])
        super(ConsoleProgressHandler, self).__init__(*args, **kwargs)

    def __enter__(self):
        self.start()
        return super(ConsoleProgressHandler, self).__enter__()

    def update(self, value=None):
        super(ConsoleProgressHandler, self).update(value)
        self.fd.flush()


class ServerProgressHandler(StateProgressHandler):
    def __init__(self, *args, **kwargs):
        self.eta = ""
        kwargs.setdefault('widgets', [])
        kwargs.setdefault('term_width', 0)
        if 'fd' not in kwargs:
            kwargs['fd'] = open(os.devnull, 'w+')
        super(ServerProgressHandler, self).__init__(*args, **kwargs)

    def eta(self):
        if self.currval == 0:
            return ''
        else:
            elapsed = self.seconds_elapsed
            eta = elapsed * self.maxval / self.currval - elapsed
            return self.format_time(eta)

progress = None


def progressToQueue(queue):
    global progress
    progress = queue


def make_progress(msg):
    global progress
    progress.put(msg)


def save_progress(key, size):
    global progress
    progress.put({'save': True, 'key': key, 'size': size})
