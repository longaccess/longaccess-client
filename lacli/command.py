from __future__ import division
import os
import cmd
import glob
import pyaml
import sys
import time
import shlex
from docopt import docopt, DocoptExit
from lacli.log import getLogger, setupLogging
from lacli.upload import Upload
from lacli.archive import restore_archive
from lacli.adf import archive_size
from time import strftime
from urlparse import urlparse
from functools import wraps


def command(**types):
    """ Decorator to parse command options with docopt and
        validate the types.
    """
    def decorate(func):
        @wraps(func)
        def wrap(self, line):
            kwargs = {}
            try:
                opts = docopt(func.__doc__, shlex.split(line))
                for opt, val in opts.iteritems():
                    kw = opt.strip('<>')
                    if val and kw in types:
                        kwargs[kw] = types[kw](val)
            except ValueError as e:
                print "error: ", e
                print func.__doc__
            except DocoptExit as e:
                print e
                return
            func(self, **kwargs)
        return wrap
    return decorate


class LaCommand(cmd.Cmd):
    prompt = 'lacli> '
    archive = None
    capsule = None
    certificate = None

    def __init__(self, session, cache, prefs):
        cmd.Cmd.__init__(self)
        setupLogging(prefs['command']['debug'])
        self.archive = LaArchiveCommand(session, cache, prefs)
        self.capsule = LaCapsuleCommand(session, cache, prefs)

    def do_EOF(self, line):
        print
        return True

    def dispatch(self, subcmd, options):
        options.insert(0, subcmd)
        subcmd = getattr(self, subcmd)
        line = subcmd.makecmd(docopt(subcmd.__doc__, options))
        if line:
            subcmd.onecmd(line)
        else:
            subcmd.cmdloop()

    def do_archive(self, line):
        self.dispatch(self.archive, line)

    def do_capsule(self, line):
        self.dispatch(self.capsule, line)

    def do_certificate(self, line):
        self.dispatch(self.certificate, line)


class LaCapsuleCommand(cmd.Cmd):
    """Manage Long Access Capsules

    Usage: lacli capsule list
           lacli capsule create <title>
           lacli capsule --help
           lacli capsule

    """
    prompt = 'capsule> '

    def __init__(self, session, cache, prefs, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.session = session
        self.verbose = prefs['command']['verbose']
        self.batch = prefs['command']['batch']
        self.cache = cache
        self.debug = prefs['command']['debug']

    def makecmd(self, options):
        line = []
        if options['list']:
            line.append("list")
        return " ".join(line)

    def do_EOF(self, line):
        print
        return True

    @command()
    def do_list(self):
        """
        Usage: list
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


class LaArchiveCommand(cmd.Cmd):
    """Upload a file to Long Access

    Usage: lacli archive upload [-n <np>] [<archive>] [<capsule>]
           lacli archive list
           lacli archive complete <archive>
           lacli archive create <dirname> -t <title>
           lacli archive extract [-o <dirname>] [<archive>] [<key>]
           lacli archive status [<upload-index>]
           lacli archive --help
           lacli archive

    Options:
        -n <np>, --procs <np>               number of processes [default: auto]
        -t <title>, --title <title>         title for prepared archive
        -o <dirname>, --out <dirname>       directory to restore archive
        -c <capsule>, --capsule <capsule>   capsule to upload to [default: 1]

    """
    prompt = 'archive> '

    def __init__(self, session, cache, prefs, uploader=None, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.session = session
        self.verbose = prefs['command']['verbose']
        self.batch = prefs['command']['batch']
        self.cache = cache
        self.debug = prefs['command']['debug']
        self.nprocs = None
        self._var = {}
        self._default_var = {
            'archive_title': lambda: strftime("%x archive"),
            'output_directory': os.getcwd()
            }

    def setopt(self, options):
        try:
            if options['--procs'] != 'auto':
                self.nprocs = int(options['--procs'])
        except ValueError:
            print "error: illegal value for 'procs' parameter."
            raise

    def do_EOF(self, line):
        print
        return True

    def makecmd(self, options):
        self.setopt(options)
        line = []
        if 'upload' in options and options['upload']:
            line.append("upload")
            if options['<archive>']:
                line.append(options['<archive>'])
            if options['<capsule>']:
                line.append(options['<capsule>'])
        elif options['list']:
            line.append("list")
        elif options['create']:
            line.append("create")
            line.append(options['<dirname>'])
            if options['--title']:
                line.append('"'+options['--title']+'"')
        return " ".join(line)

    @command(archive=int, capsule=int)
    def do_upload(self, archive=1, capsule=1):
        """
        Usage: upload [<archive>] [<capsule>]
        """
        docs = self.cache.archives(full=True)
        if capsule <= 0:
            print "Invalid capsule"
        elif archive <= 0 or len(docs) < archive:
            print "No such archive."
        else:
            capsule -= 1
            docs = docs[archive-1]
            archive = docs['archive']
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

            auth = None
            if 'auth' in docs:
                auth = docs['auth']

            if path:
                try:
                    saved = None
                    with self.session.upload(capsule, archive, auth) as upload:
                        saved = self.cache.save_upload(docs, upload)
                        Upload(self.session, self.nprocs, self.debug).upload(
                            path, upload['tokens'])

                    if saved and not self.batch:
                        print ""
                        print "Upload complete, waiting for verification"
                        print "Press Ctrl-C to check manually later"
                        while True:
                            status = self.session.upload_status(saved['link'])
                            if status['status'] == "error":
                                print "status: error"
                            elif status['status'] == "completed":
                                print "status: completed"
                                cert = self.cache.save_cert(saved, status)
                                print "Certificate:\n"
                                print cert
                            else:
                                for i in xrange(30):
                                    time.sleep(1)

                    print "\ndone."
                except Exception as e:
                    getLogger().debug("exception while uploading",
                                      exc_info=True)
                    print "error: " + str(e)

    @command(directory=str, title=str)
    def do_create(self, directory=None, title="my archive"):
        """
        Usage: create <directory> <title>
        """
        try:
            if not os.path.isdir(directory):
                print "The specified folder does not exist."
                return
            self.cache.prepare(title, directory)
            print "archive prepared"

        except Exception as e:
            getLogger().debug("exception while preparing",
                              exc_info=True)
            print "error: " + str(e)

    @command()
    def do_list(self):
        """
        Usage: list
        """
        archives = self.cache.archives(full=True)
        archives += self.cache.archives(full=True, category="uploads")

        if len(archives):
            for n, archive in enumerate(archives):
                status = "LOCAL"
                cert = ""
                if 'links' in archive:
                    if archive['links'].upload:
                        status = "UPLOADED"
                    if archive['links'].download:
                        status = "COMPLETE"
                        cert = archive['links'].download
                title = archive['archive'].title
                size = archive_size(archive['archive'])
                print "{:03d} {:>6} {:>20} {:>10} {:>10}".format(
                    n+1, size, title, status, cert)
                if self.verbose:
                    for doc in archive.itervalues():
                        pyaml.dump(doc, sys.stdout)
                    print
        else:
            print "No prepared archives."

    @command(archive=str)
    def do_complete(self, archive=None):
        uploads = self.cache.uploads()
        if archive < 0 or len(uploads) <= archive:
            print "No such upload pending."
        else:
            upload = uploads[archive]
            try:
                url = upload['link']
                status = self.session.upload_status(url)
                print "status:", status['status']
                if status['status'] == "completed":
                    cert = self.cache.save_cert(upload, status)
                    print "Certificate:\n"
                    print cert
            except Exception as e:
                getLogger().debug("exception while checking status",
                                  exc_info=True)
                print "error: " + str(e)

    @command(archive=str, key=None)
    def do_extract(self, archive=0, key=None):
        archives = self.cache.archives()
        path = None
        if archive < 0 or len(archives) <= archive:
            print "No such archive."
        else:
            archive = archives[archive]
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

                def _print(f):
                    print "Extracting", f
                restore_archive(archive, path, cert,
                                outdir,
                                self.cache._cache_dir(
                                    'tmp', write=True), _print)
                print "archive restored."
            except Exception as e:
                getLogger().debug("exception while restoring",
                                  exc_info=True)
                print "error: " + str(e)

    def complete_put(self, text, line, begidx, endidx):  # pragma: no cover
        return [os.path.basename(x) for x in glob.glob('{}*'.format(line[4:]))]
