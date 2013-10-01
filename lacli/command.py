import os
import cmd
import glob
from progressbar import (ProgressBar, Bar,
                         ETA, FileTransferSpeed)
from lacli.log import queueOpened, logHandler
from lacli.upload import UploadManager


class progressHandler(object):
    def __init__(self, fname, total):
        if total == 0:
            total = 1
        self.bar = ProgressBar(widgets=[
            fname, ' : ', Bar(),
            ' ', ETA(), ' ', FileTransferSpeed()], maxval=total)
        self.total = total
        self.tx = {}

    def handle(self, msg):
        if len(self.tx) == 0:
            self.bar.start()
        if hasattr(msg, 'part'):
            self.tx[msg['part']] = int(msg['tx'])
            self.bar.update(sum(self.tx.values()))
        else:
            self.bar.update(self.total)


class LaCommand(cmd.Cmd):
    """ Our LA command line interface"""
    prompt = 'lacli> '

    def __init__(self, session, debug=0, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.session = session
        self.debug = debug

    def do_tvmconf(self, line):
        """tvmconf
        reset TVM access configuration (key, token, etc)"""

        return True

    def do_EOF(self, line):
        return True

    def do_put(self, f):
        """Upload a file to LA [filename]
        """
        fname = f.strip()
        if not fname:
            fname = raw_input('Filename: ').strip()
        if not fname:
            print "Argument required."
        elif not os.path.isfile(fname):
            print 'File {} not found or is not a regular file.'.format(fname)
        else:
            with queueOpened(logHandler('lacli')) as q:
                with queueOpened(progressHandler(fname,
                                                 os.path.getsize(fname))) as p:
                    with UploadManager(self.session) as s:
                        s.upload(fname, q, p)
                    print ''

    def do_list(self, line):
        """List capsules in LA
        """
        capsules = self.session.capsules()

        if len(capsules):
            print "Available capsules:"
        else:
            print "No available capsules."

    def complete_put(self, text, line, begidx, endidx):
        return [os.path.basename(x) for x in glob.glob('{}*'.format(line[4:]))]
