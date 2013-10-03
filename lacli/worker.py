import sys
import os

from lacli.log import logToQueue, getLogger
from lacli.progress import progressToQueue
from multiprocessing import cpu_count, pool, current_process, Process
from setproctitle import setproctitle


def initworker(logq, progq, stdin=None):
    """initializer that sets up logging and progress from sub procs """
    logToQueue(logq)
    progressToQueue(progq)
    setproctitle(current_process().name)
    if stdin is not None:
        sys.stdin = os.fdopen(stdin, 'r')


class WorkerProcess(Process):
    def __init__(self, *args, **kwargs):
        super(WorkerProcess, self).__init__(*args, **kwargs)
        self.name = "Long Access " + self.name


class WorkerPool(pool.Pool):
    Process = WorkerProcess

    def __init__(self, prefs, logq, progq):
        nprocs = prefs['nprocs'] or max(cpu_count()-1, 1)
        args = [logq, progq]
        if prefs['debugworker']:
            args.append(sys.stdin.fileno())
        super(WorkerPool, self).__init__(nprocs, initworker, args)
        getLogger().debug("set up pool of {} procs..".format(nprocs))
