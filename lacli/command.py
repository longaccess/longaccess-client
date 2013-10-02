import os
import cmd
import glob
from progressbar import (ProgressBar, Bar,
                         ETA, FileTransferSpeed)
from lacli.log import queueOpened, logHandler, getLogger, setupLogging
from lacli.upload import Upload
from sys import maxint, stderr


class progressHandler(object):
    def __init__(self, fname):
        self.total = maxint
        if os.path.isfile(fname):
            self.total = (os.path.getsize(fname) or 1)
        self.bar = ProgressBar(widgets=[
            fname, ' : ', Bar(),
            ' ', ETA(), ' ', FileTransferSpeed()], maxval=self.total)
        self.tx = {}

    def handle(self, msg):
        if len(self.tx) == 0:
            self.bar.start()
        if 'part' in msg:
            self.tx[msg['part']] = int(msg['tx'])
            self.bar.update(sum(self.tx.values()))
        else:
            self.bar.update(self.total)
        stderr.flush()


class LaCommand(cmd.Cmd):
    """ Our LA command line interface"""
    prompt = 'lacli> '

    def __init__(self, session, prefs, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        setupLogging(prefs['command']['debug'])
        self.session = session
        self.uploader = Upload(session, prefs['upload'])

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
        elif not os.path.exists(fname):
            print 'File {} not found.'.format(fname)
        else:
            with queueOpened(logHandler('lacli')) as q:
                with queueOpened(progressHandler(fname)) as p:
                    try:
                        self.uploader.upload(fname, q, p)
                        print "\ndone."
                    except Exception as e:
                        getLogger().debug("exception while uploading",
                                          exc_info=True)
                        print "error: " + str(e)

    def do_list(self, line):
        """List capsules in LA
        """
        try:
            capsules = self.session.capsules()

            if len(capsules):
                print "Available capsules:"
            else:
                print "No available capsules."
        except Exception as e:
            print "error: " + str(e)

    def complete_put(self, text, line, begidx, endidx):
        return [os.path.basename(x) for x in glob.glob('{}*'.format(line[4:]))]
