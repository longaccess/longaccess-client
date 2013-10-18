from __future__ import division
import os
import cmd
import glob
import pyaml
import sys
import time
import shlex
from pipes import quote
from docopt import docopt, DocoptExit
from lacli.log import getLogger, setupLogging
from lacli.upload import Upload
from lacli.archive import restore_archive
from lacli.adf import archive_size
from time import strftime
from urlparse import urlparse
from functools import wraps
from lacli.main import __doc__


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
        self.certificate = LaCertsCommand(session, cache, prefs)

    def do_EOF(self, line):
        print
        return True

    def dispatch(self, subcmd, options):
        options.insert(0, subcmd)
        if not hasattr(self, subcmd):
            print(__doc__)
            raise SystemExit
        subcmd = getattr(self, subcmd)
        try:
            line = subcmd.makecmd(docopt(subcmd.__doc__, options))
            self.dispatch_one(subcmd, line)
        except DocoptExit as e:
            print e
            return

    def dispatch_one(self, subcmd, line, interactive=False):
        if line:
            subcmd.onecmd(line)
        elif interactive:
            subcmd.cmdloop()

    def do_archive(self, line):
        self.dispatch_one(self.archive, line, True)

    def do_capsule(self, line):
        self.dispatch_one(self.capsule, line, True)

    def do_certificate(self, line):
        self.dispatch_one(self.certificate, line, True)


class LaCertsCommand(cmd.Cmd):
    """Manage Long Access Certificates

    Usage: lacli certificate list
           lacli certificate export <cert_id>
           lacli certificate import <filename>
           lacli certificate delete <cert_id> [<srm>...]
           lacli certificate --help

    """
    prompt = 'lacli:certificate> '

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
        elif options['delete']:
            line.append("delete")
            line.append(options["<cert_id>"])
            if options['<srm>']:
                line.append(quote(
                    " ".join(options["<srm>"])))
        elif options['export']:
            line.append("export")
            line.append(options["<cert_id>"])
        elif options['import']:
            line.append("import")
            line.append(options["<filename>"])
        return " ".join(line)

    def do_EOF(self, line):
        print
        return True

    @command()
    def do_list(self):
        """
        Usage: list
        """
        certs = self.cache._for_adf('certs')

        if len(certs):
            for n, cert in enumerate(certs.iteritems()):
                cert = cert[1]
                id = ""
                if 'links' in cert:
                    if cert['links'].download:
                        id = cert['links'].download
                title = cert['archive'].title
                size = archive_size(cert['archive'])
                print "{:>10} {:>6} {:<}".format(
                    id, size, title)
                if self.verbose:
                    for doc in cert.itervalues():
                        pyaml.dump(doc, sys.stdout)
                    print
        else:
            print "No available certificates."

    @command(cert_id=str, srm=str)
    def do_delete(self, cert_id=None, srm=None):
        """
        Usage: delete <cert_id> [<srm>]
        """
        srmprompt = "\n".join((
            "WARNING! Insecure deletion attempt.",
            "Could not find a secure deletion command",
            "The certificate you are about to delete may still recoverable.",
            "For more information see: https://ssd.eff.org/tech/deletion"))
        fileprompt = "\n".join((
            "Please provide a valid srm command as an option or remove the",
            "file manually:"))

        def _countdown():
            print "Deleting certificate", cert_id, "in 5",
            for num in [4, 3, 2, 1]:
                sys.stdout.flush()
                time.sleep(1)
                sys.stdout.write(", {}".format(num))
                yield ""
            print "... deleting"

        fname = self.cache.shred_cert(cert_id, _countdown(), srm)
        if not fname:
            print "Certificate not found"
        elif os.path.exists(fname):
            if not srm:
                print srmprompt
            else:
                print srm, "failed."
            print fileprompt
            print fname
        else:
            print "Deleted certificate", cert_id

    @command(cert_id=str)
    def do_export(self, cert_id=None):
        """
        Usage: export <cert_id>
        """
        path = self.cache.print_cert(cert_id)
        if path:
            print "Created files:"
            print path[0]
            print path[1]
        else:
            print "Certificate not found"

    @command(filename=str)
    def do_import(self, filename=None):
        """
        Usage: import <filename>
        """
        certs = self.cache.certs([filename])
        if len(certs) > 0:
            for key, cert in certs.iteritems():
                if key in self.cache.certs():
                    print "Certificate", key, "already exists"
                else:
                    print "Imported certificate {}".format(
                        self.cache.import_cert(filename))
        else:
            print "No certificates found in", filename


class LaCapsuleCommand(cmd.Cmd):
    """Manage Long Access Capsules

    Usage: lacli capsule list
           lacli capsule create <title>
           lacli capsule --help

    """
    prompt = 'lacli:capsule> '

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

    Usage: lacli archive upload [-n <np>] [<index>] [<capsule>]
           lacli archive list
           lacli archive status <index>
           lacli archive create <dirname> -t <title>
           lacli archive extract [-o <dirname>] <path> (<cert_id>|-f <cert>)
           lacli archive delete <index> [<srm>...]
           lacli archive --help

    Options:
        -n <np>, --procs <np>               number of processes [default: auto]
        -t <title>, --title <title>         title for prepared archive
        -o <dirname>, --out <dirname>       directory to restore archive
        -c <capsule>, --capsule <capsule>   capsule to upload to [default: 1]
        -f <cert>, --cert <cert>            certificate file to use
        -h, --help                          this help

    """
    prompt = 'lacli:archive> '

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
            if options['<index>']:
                line.append(options['<index>'])
            if options['<capsule>']:
                line.append(options['<capsule>'])
        elif options['list']:
            line.append("list")
        elif options['create']:
            line.append("create")
            line.append(options['<dirname>'])
            if options['--title']:
                line.append('"'+options['--title']+'"')
        elif options['status']:
            line.append("status")
            line.append(options['<index>'])
        elif options['extract']:
            line.append("extract")
            line.append(options['<path>'])
            if options['--out']:
                line.append(quote(options['--out']))
            else:
                line.append(os.getcwd())
            if options['--cert']:
                line.append("dummy")
                line.append(quote(options['--cert']))
            else:
                line.append(options['<cert_id>'])
        elif options['delete']:
            line.append("delete")
            line.append(options["<index>"])
            if options['<srm>']:
                line.append(quote(
                    " ".join(options["<srm>"])))
        return " ".join(line)

    @command(index=int, capsule=int)
    def do_upload(self, index=1, capsule=1):
        """
        Usage: upload [<index>] [<capsule>]
        """
        docs = list(self.cache._for_adf('archives').iteritems())

        if capsule <= 0:
            print "Invalid capsule"
        elif index <= 0 or len(docs) < index:
            print "No such archive."
        else:
            capsule -= 1
            fname = docs[index-1][0]
            docs = docs[index-1][1]
            archive = docs['archive']
            link = docs['links']
            path = ''
            if link.upload or link.download:
                print "upload is already completed"
            elif link.local:
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
                        Upload(self.session, self.nprocs, self.debug).upload(
                            path, upload['tokens'])
                        saved = self.cache.save_upload(fname, docs, upload)

                    if saved and not self.batch:
                        print ""
                        print "Upload finished, waiting for verification"
                        print "Press Ctrl-C to check manually later"
                        while True:
                            status = self.session.upload_status(saved['link'])
                            if status['status'] == "error":
                                print "status: error"
                                break
                            elif status['status'] == "completed":
                                print "status: completed"
                                fname = saved['fname']
                                cert = self.cache.save_cert(
                                    self.cache.upload_complete(fname, status))
                                print "Certificate", cert, "saved.\n"
                                print " ".join(("Use lacli certificate list",
                                                "to see your certificates, or",
                                                "lacli certificate --help for",
                                                "more options"))
                                break
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
        archives = self.cache._for_adf('archives')

        if len(archives):
            for n, archive in enumerate(archives.iteritems()):
                archive = archive[1]
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

    @command(index=int)
    def do_status(self, index=1):
        """
        Usage: status <index>
        """
        docs = list(self.cache._for_adf('archives').iteritems())
        if index <= 0 or len(docs) < index:
            print "No such archive"
        else:
            fname = docs[index-1][0]
            upload = docs[index-1][1]
            if not upload['links'].upload:
                if upload['links'].download:
                    print "status: complete"
                else:
                    print "status: local"
            else:
                try:
                    url = upload['links'].upload
                    status = self.session.upload_status(url)
                    print "status:", status['status']
                    if status['status'] == "completed":
                        cert = self.cache.save_cert(
                            self.cache.upload_complete(fname, status))
                        print "Certificate", cert, "saved.\n"
                        print " ".join(("Use lacli certificate list",
                                        "to see your certificates, or",
                                        "lacli certificate --help for",
                                        "more options"))
                except Exception as e:
                    getLogger().debug("exception while checking status",
                                      exc_info=True)
                    print "error: " + str(e)

    @command(path=str, dest=str, cert_id=str, cert_file=str)
    def do_extract(self, path=None, dest=None, cert_id=None, cert_file=None):
        """
        Usage: extract <path> <dest> <cert_id> [<cert_file>]
        """
        if cert_file:
            certs = self.cache.certs([cert_file])
            cert_id = next(certs.iterkeys())
        else:
            certs = self.cache.certs()

        path = os.path.expanduser(path)
        dest = os.path.expanduser(dest)
        if cert_file:
            cert_file = os.path.expanduser(cert_file)

        if cert_id not in certs:
            print "no matching certificate found"
        elif not os.path.isfile(path):
            print "error: file", path, "does not exist"
        elif not os.path.isdir(dest):
            print "output directory", dest, "does not exist"
        else:
            cert = certs[cert_id]['cert']
            archive = certs[cert_id]['archive']
            try:
                def _print(f):
                    print "Extracting", f
                restore_archive(archive, path, cert,
                                dest,
                                self.cache._cache_dir(
                                    'tmp', write=True), _print)
                print "archive restored."
            except Exception as e:
                getLogger().debug("exception while restoring",
                                  exc_info=True)
                print "error: " + str(e)

    def complete_put(self, text, line, begidx, endidx):  # pragma: no cover
        return [os.path.basename(x) for x in glob.glob('{}*'.format(line[4:]))]

    @command(index=int, srm=str)
    def do_delete(self, index=None, srm=None):
        """
        Usage: delete <index> [<srm>]
        """
        docs = list(self.cache._for_adf('archives').iteritems())

        if index <= 0 or len(docs) < index:
            print "No such archive."
        else:
            fname = docs[index-1][0]
            docs = docs[index-1][1]
            archive = docs['archive']
            link = docs['links']
            path = ''
            if link.local:
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

        srmprompt = "\n".join((
            "WARNING! Insecure deletion attempt.",
            "Could not find a secure deletion command",
            "The archive you are about to delete may still recoverable.",
            "For more information see: https://ssd.eff.org/tech/deletion"))
        fileprompt = "\n".join((
            "Please provide a valid srm command as an option or remove the",
            "file(s) manually:"))

        print "Deleting archive", index, "({}) in 5".format(archive.title),
        for num in [4, 3, 2, 1]:
            sys.stdout.flush()
            time.sleep(1)
            sys.stdout.write(", {}".format(num))
        print "... deleting"

        self.cache.shred_file(fname, srm)
        if os.path.exists(fname):
            if not srm:
                print srmprompt
            else:
                print srm, "failed."
            print fileprompt
            print fname
            if path:
                print path
        else:
            if path:
                self.cache.shred_file(path, srm)
            if os.path.exists(path):
                print "ERROR: Failed to delete archive data:", path
                print "Please remove manually"
            else:
                print "Deleted archive", archive.title
