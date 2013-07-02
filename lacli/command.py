import os
import cmd
from lacli.upload import pool_upload

class LaCommand(cmd.Cmd):
    """ Our LA command line interface"""
    prompt='lacli> '  

    def __init__(self, options, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.options=options

    def do_tvmconf(self, line):
        """tvmconf
        reset TVM access configuration (key, token, etc)"""

        return True

    def do_EOF(self, line):
        return True

    def do_put(self, fname):
        if not os.path.isfile(fname):
            print 'File {} not found.'.format(fname)
        else:
            pool_upload(self.options.user, self.options.duration, fname)

	
