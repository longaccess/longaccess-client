import os

from urlparse import urlparse
from netrc import netrc
from lacli.log import getLogger
from lacli.decorators import cached_property


API_URL = 'https://www.longaccess.com/api/v1/'


class LaRegistry(object):
    cache = None
    prefs = None
    session = None

    def __init__(self, cache, prefs, cmd):
        self.cache = cache
        self.prefs = prefs
        self.cmd = cmd
        self.session = self.new_session()

    def new_session(self, prefs=None):
        if not prefs:
            prefs = self.prefs['api']
        if prefs.get('url') is None:
            prefs['url'] = API_URL
        if not prefs['user']:
            prefs['user'] = self._saved_session[0]
            prefs['pass'] = self._saved_session[1]
        return self.prefs['api']['factory'](prefs)

    @cached_property
    def _saved_session(self):
        hostname = urlparse(self.prefs['api']['url']).hostname
        try:
            for host, creds in netrc().hosts.iteritems():
                if host == hostname:
                    return (creds[0], creds[2])
        except:
            getLogger().debug("Couldn't read from netrc", exc_info=True)
        return (None, None)

    def save_session(self, *args):
        self._saved_session = tuple(args)
        with open(os.path.expanduser("~/.netrc"), 'a') as f:
            f.write("machine {} login {} password {}\n".format(
                urlparse(self.session.url).hostname,
                self._saved_session[0],
                self._saved_session[1]))
