import os
import cmd
import glob
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

    def do_put(self, f):
        fname=f.strip()
        if not fname:
            fname=raw_input('Filename: ').strip()
        if not os.path.isfile(fname):
            print 'File {} not found or is not a directory.'.format(fname)
        else:
            pool_upload(self.options.user, self.options.duration, fname)
    def complete_put(self, text, line, begidx, endidx):
        return [os.path.basename(x) for x in glob.glob('{}*'.format(line[4:]))]

	
