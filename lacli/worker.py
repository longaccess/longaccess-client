from lacli.log import logToQueue, getLogger
from lacli.progress import progressToQueue
from multiprocessing import cpu_count, pool, current_process, Process
from setproctitle import setproctitle


def initworker(logq, progq):
    """initializer that sets up logging and progress from sub procs """
    logToQueue(logq)
    progressToQueue(progq)
    setproctitle(current_process().name)


class WorkerProcess(Process):
    def __init__(self, *args, **kwargs):
        super(WorkerProcess, self).__init__(*args, **kwargs)
        self.name = "Long Access " + self.name


class WorkerPool(pool.Pool):
    Process = WorkerProcess

    def __init__(self, prefs, logq, progq):
        nprocs = prefs['nprocs'] or max(cpu_count()-1, 1)
        args = (nprocs, initworker, (logq, progq))
        super(WorkerPool, self).__init__(*args)
        getLogger().debug("set up pool of {} procs..".format(nprocs))
