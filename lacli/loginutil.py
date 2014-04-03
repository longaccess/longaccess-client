from functools import update_wrapper, wraps
from twisted.internet import defer
from lacli.log import getLogger


class login_async(object):
    def __init__(self, f, obj=None):
        self.f = f
        self.obj = obj
        update_wrapper(self, self.f)

    def __get__(self, obj, cls):
        return wraps(self.f)(login(self.f, obj))

    def dologin(self, prefs):
        return self.obj.registry.cmd.login.login_async(
            prefs.get('user'), prefs.get('pass'))

    @defer.inlineCallbacks
    def loginfirst(self, prefs, *args, **kwargs):
        try:
            yield self.dologin(prefs)
            r = yield self.f(self.obj, *args, **kwargs)
            defer.returnValue(r)
        except Exception:
            getLogger().debug("unhandled error in login decorator",
                              exc_info=True)
            raise

    def __call__(self, *args, **kwargs):
        if len(args) > 0:
            if self.obj is None:
                self.obj = args[0]
                args = args[1:]
            elif self.obj == args[0]:
                args = args[1:]

        prefs = None
        if self.obj.registry.session:
            prefs = self.obj.registry.session.prefs
        if not prefs:
            prefs = self.obj.registry.init_prefs()

        if not self.obj.session or self.obj.registry.cmd.login.email is None:
            return self.loginfirst(prefs, *args, **kwargs)
        return self.f(self.obj, *args, **kwargs)


class login(login_async):
    def __init__(self, *args, **kwargs):
        super(login, self).__init__(*args, **kwargs)

    def dologin(self, prefs):
        if self.obj.batch:
            self.obj.registry.cmd.login.login_batch(
                prefs.get('user'), prefs.get('pass'))
        else:
            cmdline = [prefs[a] for a in ['user', 'pass']
                       if prefs.get(a)]
            self.obj.registry.cmd.username = prefs['user']
            self.obj.registry.cmd.password = prefs['pass']
            self.obj.registry.cmd.do_login(" ".join(cmdline))

    def loginfirst(self, prefs, *args, **kwargs):
        self.dologin(prefs)
        return self.f(self.obj, *args, **kwargs)
