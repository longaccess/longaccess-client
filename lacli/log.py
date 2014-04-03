import lacore.log


def setupLogging(level=0, logfile=None):
    ctx = lacore.log.setupLogging(level, logfile)
    lacore.log.getLogger('lacli').addHandler(
        lacore.log.getLogger('lacore').handlers[0])
    return ctx


def getLogger(logger='lacli'):
    return lacore.log.getLogger(logger)
