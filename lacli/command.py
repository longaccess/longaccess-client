import os
import cmd
import glob
from lacli.upload import pool_upload
from lacli.log import queueOpened, logToQueue

class LaCommand(cmd.Cmd):
    """ Our LA command line interface"""
    prompt='lacli> '  

    def __init__(self, session, debug=0, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.session=session
        self.debug=debug

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
            with queueOpened() as q:
                def initlog():
                    logToQueue(self.debug, q)
                pool_upload(fname, self.session.tokens, initlog)
                
    def complete_put(self, text, line, begidx, endidx):
        return [os.path.basename(x) for x in glob.glob('{}*'.format(line[4:]))]

	
