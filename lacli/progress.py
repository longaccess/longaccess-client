import os
from sys import maxint, stderr
from progressbar import (ProgressBar, Bar,
                         ETA, FileTransferSpeed)
from lacli.log import queueHandler


class ProgressHandler(queueHandler):
    def __init__(self, fname):
        self.total = maxint
        if os.path.isfile(fname):
            self.total = (os.path.getsize(fname) or 1)
        self.bar = ProgressBar(widgets=[
            fname, ' : ', Bar(),
            ' ', ETA(), ' ', FileTransferSpeed()], maxval=self.total)
        self.tx = {}
        self.previous = 0

    def handle(self, msg):
        progress = self.previous
        if len(self.tx) == 0:
            self.bar.start()
        if 'complete' in msg:
            progress = self.total
        elif 'part' in msg:
            self.tx[msg['part']] = int(msg['tx'])
            progress += sum(self.tx.values())
        elif 'save' in msg:
            self.previous += sum(self.tx.values())
            progress = self.previous
            self.tx = {}
        self.bar.update(progress)
        stderr.flush()

    def __enter__(self):
        q = super(ProgressHandler, self).__enter__()
        progressToQueue(q)
        return q

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
