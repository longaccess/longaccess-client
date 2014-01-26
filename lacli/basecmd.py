import sys
import signal
import cmd
from abc import ABCMeta, abstractmethod


class LaBaseCommand(cmd.Cmd, object):
    __metaclass__ = ABCMeta

    prompt = 'lacli> '

    def __init__(self, registry, *args, **kwargs):
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, signal.default_int_handler)
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.registry = registry

    @property
    def verbose(self):
        return self.registry.prefs['command']['verbose']

    @property
    def safe(self):
        return not self.registry.prefs['command']['unsafe']

    @property
    def batch(self):
        return self.registry.prefs['command']['batch']

    @batch.setter
    def batch(self, newvalue):
        self.registry.prefs['command']['batch'] = newvalue

    @property
    def cache(self):
        return self.registry.cache

    @property
    def debug(self):
        return self.registry.prefs['command']['debug']

    @property
    def prefs(self):
        return self.registry.prefs

    @property
    def session(self):
        return self.registry.session

    @session.setter
    def session(self, newsession):
        self.registry.session = newsession

    @abstractmethod
    def makecmd(self, options):
        """ Parse docopt style options and return a cmd-style line """

    def do_EOF(self, line):
        print
        return True

    def input(self, prompt=""):
        sys.stdout.write(prompt)
        line = sys.stdin.readline()
        if line:
            return line.strip()


