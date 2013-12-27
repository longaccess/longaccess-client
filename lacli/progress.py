import os
from sys import maxint, stderr
from progressbar import (ProgressBar, Bar,
                         ETA, FileTransferSpeed)
from lacli.log import queueHandler, getLogger
from abc import ABCMeta, abstractmethod


class BaseProgressHandler(queueHandler):
    __metaclass__ = ABCMeta

    def __init__(self, size=None):
        self.total = size
        self.tx = {}
        self.progress = 0

    def update_current(self, msg):
        self.tx[msg['part']] = int(msg['tx'])
        return sum(self.tx.values())

    def save_current(self):
        self.progress += sum(self.tx.values())
        self.tx = {}
        return self.progress

    def handle(self, msg):
        progress = self.progress
        if 'complete' in msg:
            progress = self.total
        elif 'part' in msg:
            progress += self.update_current(msg)
        elif 'save' in msg:
            self.keydone(msg)
            progress = self.save_current()
        self.update(progress)

    def __enter__(self):
        q = super(BaseProgressHandler, self).__enter__()
        progressToQueue(q)
        return q

    @abstractmethod
    def update(self, progress):
        getLogger().debug("got progress: " + str(progress))

    @abstractmethod
    def keydone(self, msg):
        getLogger().debug("saved key: " + str(msg['key'])
            + " (" + str(msg['size']) + ")")


class ServerProgressHandler(BaseProgressHandler):
    def __init__(self, state=None, **kwargs):
        assert state is not None, "ServerProgressHandler requires a state object"
        self.state = state
        super(ServerProgressHandler, self).__init__(**kwargs)
        for seq, key in enumerate(self.state.keys):
            self.progress += key['size']
        
    def update(self, progress):
        self.state.update(progress)

    def keydone(self, msg):
        getLogger().debug("saving key " + str(msg['key']) + " to state file")
        self.state.keydone(msg['key'], msg['size'])


class ConsoleProgressHandler(ServerProgressHandler):
    def __init__(self, *args, **kwargs):
        fname = kwargs.pop('fname', "-")
        self.bar = ProgressBar(widgets=[
            fname, ' : ', Bar(),
            ' ', ETA(), ' ', FileTransferSpeed()], maxval=kwargs.get('size'))
        super(ConsoleProgressHandler, self).__init__(*args, **kwargs)

    def __enter__(self):
        self.bar.start()
        return super(ConsoleProgressHandler, self).__enter__()

    def update(self, progress):
        super(ConsoleProgressHandler, self).update(progress)
        self.bar.update(progress)
        stderr.flush()

    def keydone(self, msg):
        super(ConsoleProgressHandler, self).keydone(msg)


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
