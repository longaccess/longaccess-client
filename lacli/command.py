import os
import cmd
import glob
from lacli.upload import pool_upload

class LaCommand(cmd.Cmd):
    """ Our LA command line interface"""
    prompt='lacli> '  

    def __init__(self, session, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.session=session

    def do_tvmconf(self, line):
        """tvmconf
        reset TVM access configuration (key, token, etc)"""

        return True

    def do_EOF(self, line):
        return True

    def do_put(self, f):
        """Upload a file to LA [filename]
        """
        fname=f.strip()
        if not fname:
            fname=raw_input('Filename: ').strip()
        if not fname:
            print "Argument required."
        elif not os.path.isfile(fname):
            print 'File {} not found or is not a regular file.'.format(fname)
        else:
            pool_upload(fname, self.session.tokens)
    def complete_put(self, text, line, begidx, endidx):
        return [os.path.basename(x) for x in glob.glob('{}*'.format(line[4:]))]

	
