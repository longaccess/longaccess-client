import sys
import os
import signal

from lacli.log import logToQueue, getLogger
from lacli.progress import progressToQueue
from lacli.control import controlByQueue
from multiprocessing import cpu_count, pool, current_process, Process
try:
    from setproctitle import setproctitle
except ImportError:
    setproctitle = lambda x: x


def initworker(logq, progq, ctrlq, stdin=None):
    """initializer that sets up logging and progress from sub procs """
    logToQueue(logq)
    progressToQueue(progq)
    controlByQueue(ctrlq)
    setproctitle(current_process().name)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if hasattr(signal, 'SIGBREAK'):
        signal.signal(signal.SIGBREAK, signal.SIG_IGN)
    getLogger().debug("Worker " + current_process().name + " logging started")
    if stdin is not None:
        sys.stdin = os.fdopen(stdin, 'r')
        print "Worker " + current_process().name + " opened stdin"


class WorkerProcess(Process):
    def __init__(self, *args, **kwargs):
        super(WorkerProcess, self).__init__(*args, **kwargs)
        self.name = "Long Access " + self.name


class WorkerPool(pool.Pool):
    Process = WorkerProcess

    def __init__(self, prefs, logq, progq, ctrlq):
        nprocs = prefs['nprocs'] or max(cpu_count()-1, 1)
        args = [logq, progq, ctrlq]
        if prefs['debugworker']:
            args.append(sys.stdin.fileno())
        super(WorkerPool, self).__init__(nprocs, initworker, args)
        getLogger().debug("set up pool of {} procs..".format(nprocs))
# vim: et:sw=4:ts=4
