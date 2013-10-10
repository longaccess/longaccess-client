import os
import cmd
import glob
from lacli.log import getLogger, setupLogging
from lacli.upload import Upload
from time import strftime
from contextlib import contextmanager


class LaCommand(cmd.Cmd):
    """ Our LA command line interface"""
    prompt = 'lacli> '

    def __init__(self, session, cache, prefs, uploader=None, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        setupLogging(prefs['command']['debug'])
        self.session = session
        self.cache = cache
        if not uploader:
            self.uploader = Upload(session, prefs['upload'])
        else:
            self.uploader = uploader
        self._var = {}
        self._default_var = {'archive_title': lambda: strftime("%x archive")}

    def do_EOF(self, line):
        return True

    def do_put(self, f):
        """Upload a file to LA [filename]
        """
        fname = f.strip()
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

        d = line.strip()
        try:
            if d:
                if not os.path.isdir(d):
                    print "The specified folder does not exist."
                    return
                title = None
                if 'archive_title' in self._var:
                    title = self._var["archive_title"]
                    self.cache.prepare(title, d)
                    print "archive prepared"
            else:
                archives = self.cache.archives()

                if len(archives):
                    print "Prepared archives:"
                    for n, archive in enumerate(archives):
                        lines = (('desc:', archive.description),
                                 ('tags:', ", ".join(archive.tags)),
                                 ('type:', archive.meta.format))
                        print "{}) {}".format(n+1, archive.title)
                        for line in lines:
                            print "{:<7}{:<30}".format(line[0], line[1])
                else:
                    print "No prepared archives."
        except Exception as e:
            getLogger().debug("exception while preparing",
                              exc_info=True)
            print "error: " + str(e)

    def do_restore(self, line):
        a = line.strip()
        archives = self.cache.archives()
        if not a:
            a = 1
        if a > len(archives):
            print "No such archive."
        else:
            archive = archives[a-1]
            cert = self.cache.certs().get(archive.title)
            if cert:
                print "archive restored."
            else:
                print "no matching certificate found"

    def complete_put(self, text, line, begidx, endidx):  # pragma: no cover
        return [os.path.basename(x) for x in glob.glob('{}*'.format(line[4:]))]

    @contextmanager
    def temp_var(self, **kwargs):
        """ replace vars with the values from kwargs and
            restore original condition after """
        old = {}
        for k, v in kwargs.iteritems():
            if k in self._var:
                old[k] = self._var.pop(k)
            if not v and k in self._default_var:
                if hasattr(self._default_var[k], '__call__'):
                    v = self._default_var[k]()
                else:
                    v = self._default_var[k]
            self._var[k] = v
        yield self
        for k, v in kwargs.iteritems():
            if k in self._var:
                del self._var[k]
        self._var.update(old)
