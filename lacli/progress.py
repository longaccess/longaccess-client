import os
from sys import maxint, stderr
from progressbar import (ProgressBar, Bar,
                         ETA, FileTransferSpeed)
from lacli.log import queueHandler, getLogger
from abc import ABCMeta, abstractmethod


class BaseProgressHandler(queueHandler):
    __metaclass__ = ABCMeta

    def __init__(self, size):
        self.total = size
        self.tx = {}
        self.previous = 0

    def handle(self, msg):
        progress = self.previous
        if 'complete' in msg:
            progress = self.total
        elif 'part' in msg:
            self.tx[msg['part']] = int(msg['tx'])
            progress += sum(self.tx.values())
        elif 'save' in msg:
            self.previous += sum(self.tx.values())
            progress = self.previous
            self.tx = {}
        self.update(progress)

    def __enter__(self):
        q = super(BaseProgressHandler, self).__enter__()
        progressToQueue(q)
        return q

    @abstractmethod
    def update(self, progress):
	getLogger().debug("got progress: " + str(progress))


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


progress = None


def progressToQueue(queue):
    global progress
    progress = queue


def make_progress(msg):
    global progress
    progress.put(msg)


def save_progress():
    global progress
    progress.put({'save': True})
