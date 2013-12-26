from twisted.python.failure import Failure
from twisted.internet import reactor
from Queue import Queue, Empty
from lacli.exceptions import Timeout
from crochet import no_setup, wait_for_reactor
no_setup()

def foo(*args, **kwargs):
    import pdb; pdb.set_trace()

def block(d, timeout=None):
    if not reactor.running:
        reactor.run()
    @wait_for_reactor
    def _block(d):
        return d
    return _block(d)
    q = Queue()
    d.addBoth(q.put)
    d.addBoth(foo)
    try:
        ret = q.get(True, timeout)
    except Empty:
        raise Timeout
    except Exception as e:
        import pdb; pdb.set_trace()
        raise e
    if isinstance(ret, Failure):
        ret.raiseException()
    else:
        return ret
# vim: et:sw=4:ts=4
