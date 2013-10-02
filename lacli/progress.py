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

    def handle(self, msg):
        if len(self.tx) == 0:
            self.bar.start()
        if 'part' in msg:
            self.tx[msg['part']] = int(msg['tx'])
            self.bar.update(sum(self.tx.values()))
        else:
            self.bar.update(self.total)
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


def complete_progress():
    global progress
    progress.put({})
