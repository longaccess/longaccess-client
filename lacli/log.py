import lacore.log


def setupLogging(level=0, logfile=None):
    ctx = lacore.log.setupLogging(level, logfile)
    getLogger().addHandler(
        getLogger('lacore').handlers[0])
    getLogger().propagate = True
    getLogger().disabled = False
    return ctx


def getLogger(logger='lacli'):
    return lacore.log.getLogger(logger)
