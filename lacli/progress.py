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
        self.previous = 0

    def update_current(self, msg):
        self.tx[msg['part']] = int(msg['tx'])
        return sum(self.tx.values())

    def save_current(self):
        self.progress += sum(self.tx.values())
        self.tx = {}
        return self.progress

    def handle(self, msg):
        progress = self.previous
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
        getLogger().debug("saved key: " + str(msg.key)
            + " (" + str(msg.size) + ")")


class ConsoleProgressHandler(BaseProgressHandler):
    def __init__(self, *args, **kwargs):
        fname = kwargs.pop('fname', "-")
        super(ConsoleProgressHandler, self).__init__(*args, **kwargs)
        self.bar = ProgressBar(widgets=[
            fname, ' : ', Bar(),
            ' ', ETA(), ' ', FileTransferSpeed()], maxval=self.total)

    def handle(self, msg):
        if len(self.tx) == 0:
            self.bar.start()
        super(ConsoleProgressHandler, self).handle(msg)

    def update(self, progress):
        self.bar.update(progress)
        stderr.flush()

    def keydone(self, msg):
        super(ConsoleProgressHandler, self).save(msg)


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
