import os
from lacli.log import getLogger
from lacli.exceptions import PauseEvent
from multiprocessing import Queue, active_children
from Queue import Empty


class ControlHandler(object):

    def __init__(self):
        self.q = None

    def __enter__(self):
        self.q = Queue()
        controlByQueue(self.q)
        return self.q

    def __exit__(self, type, value, traceback):
        getLogger().debug("control handler exiting.")
        if type == KeyboardInterrupt:
            getLogger().debug("upload pausing.")
            self.pause()
            type = None
        stopControlByQueue()
        return type is None

    def pause(self):
        if self.q is not None:
            children = len(active_children())
            getLogger().debug(
               "ControlHandler pausing {} children".format(children))
            map(self.q.put, [{'pause': True}] * children)
        else:
            getLogger().debug(
               "ControlHandler.pause() called " +
               "when no control context in effect")
                

controlq = None


def controlByQueue(queue):
    global controlq
    controlq = queue


def stopControlByQueue():
    global controlq
    controlq = None

def readControl():
    global controlq
    try:
        msg = controlq.get(False)
        if 'pause' in msg:
            raise PauseEvent()
    except Empty:
        pass
# vim: et:sw=4:ts=4
