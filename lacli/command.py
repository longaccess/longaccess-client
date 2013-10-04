import os
import cmd
import glob
from lacli.log import getLogger, setupLogging
from lacli.upload import Upload


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
            try:
                self.uploader.upload(fname)
                print "\ndone."
            except Exception as e:
                getLogger().debug("exception while uploading",
                                  exc_info=True)
                print "error: " + str(e)

    def do_list(self, line):
        """List capsules in LA
        """
        try:
            capsules = list(self.session.capsules())

            if len(capsules):
                print "Available capsules:"
                for capsule in capsules:
                    print "{:<10}:{:>10}".format('title', capsule.pop('title'))
                    for i, v in capsule.iteritems():
                        print "{:<10}:{:>10}".format(i, v)
                    print "\n"
            else:
                print "No available capsules."
        except Exception as e:
            print "error: " + str(e)

    def do_archive(self, line):
        """List or manage prepared archives"""

        print "No prepared archives."

    def complete_put(self, text, line, begidx, endidx):
        return [os.path.basename(x) for x in glob.glob('{}*'.format(line[4:]))]
