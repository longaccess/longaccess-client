import os
import cmd
import glob
from lacli.log import getLogger, setupLogging
from lacli.upload import Upload
from lacli.archive import restore_archive
from time import strftime
from contextlib import contextmanager
from urlparse import urlparse


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
        self._default_var = {
            'archive_title': lambda: strftime("%x archive"),
            'output_directory': os.getcwd()
            }

    def do_EOF(self, line):
        return True

    def do_put(self, line):
        """Upload a file to LA [filename]
        """
        archives = self.cache.archives()
        line = line.strip()
        idx = None
        if not line:
            idx = 0
        else:
            try:
                idx = int(line)-1
            except ValueError:
                pass
        if idx < 0 or len(archives) <= idx:
            print "No such archive."
        else:
            archive = archives[idx]
            link = self.cache.links().get(archive.title)
            path = ''
            if link and hasattr(link, 'local'):
                parsed = urlparse(link.local)
                if parsed.scheme == 'file':
                    if os.path.exists(parsed.path):
                        path = parsed.path
                    else:
                        print 'File {} not found.'.format(parsed.path)
                else:
                    print "url not local: " + link.local
            else:
                print "no local copy exists."

            if path:
                try:
                    capsule = self._var['capsule'] - 1
                    with self.session.upload(capsule, archive) as tokens:
                        self.uploader.upload(path, tokens)
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
        path = None
        if not a:
            a = 1
        if a > len(archives):
            print "No such archive."
        else:
            archive = archives[a-1]
            cert = self.cache.certs().get(archive.title)
            if cert:
                link = self.cache.links().get(archive.title)
                if link and link.local:
                    parsed = urlparse(link.local)
                    if parsed.scheme == 'file':
                        path = parsed.path
                    else:
                        print "url not local: " + link.local
                else:
                    print "no local copy exists yet."
            else:
                print "no matching certificate found"
        if path:
            if 'output_directory' in self._var:
                outdir = self._var['output_directory']
            else:
                outdir = os.getcwd()
            try:
                restore_archive(archive, path, cert,
                                outdir,
                                self.cache._cache_dir(
                                    'tmp', write=True))
                print "archive restored."
            except Exception as e:
                getLogger().debug("exception while uploading",
                                  exc_info=True)
                print "error: " + str(e)
        else:
            print "data file {} not found."

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
