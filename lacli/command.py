from __future__ import division
import signal
import os
import cmd
import glob
import pyaml
import sys
import time
import operator
from pipes import quote
from lacli.log import getLogger
from lacli.upload import Upload, UploadState
from lacli.archive import restore_archive
from lacli.adf import archive_size, Certificate, Archive, Meta, creation
from lacli.decorators import command, login, block
from lacli.exceptions import DecryptionError
from lacli.compose import compose
from lacli.progress import ConsoleProgressHandler
from twisted.internet import defer, reactor, task
from contextlib import contextmanager
from abc import ABCMeta, abstractmethod

from richtext import RichTextUI as UIClass
ui = UIClass()

class LaBaseCommand(cmd.Cmd, object):
    __metaclass__ = ABCMeta

    prompt = 'lacli> '

    def __init__(self, registry, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.registry = registry

    @property
    def verbose(self):
        return self.registry.prefs['command']['verbose']

    @property
    def batch(self):
        return self.registry.prefs['command']['batch']

    @batch.setter
    def batch(self, newvalue):
        self.registry.prefs['command']['batch'] = newvalue

    @property
    def cache(self):
        return self.registry.cache

    @property
    def debug(self):
        return self.registry.prefs['command']['debug']

    @property
    def prefs(self):
        return self.registry.prefs

    @property
    def session(self):
        return self.registry.session

    @session.setter
    def session(self, newsession):
        self.registry.session = newsession

    @abstractmethod
    def makecmd(self, options):
        """ Parse docopt style options and return a cmd-style line """

    def do_EOF(self, line):
        print
        return True

    def input(self, prompt=""):
        sys.stdout.write(prompt)
        line = sys.stdin.readline()
        if line:
            return line.strip()


class LaCertsCommand(LaBaseCommand):
    """Manage Long Access Certificates

    Usage: lacli certificate list
           lacli certificate print <cert_id>
           lacli certificate export <cert_id>
           lacli certificate import <filename>
           lacli certificate delete <cert_id> [<srm>...]
           lacli certificate --help

    """
    prompt = 'lacli:certificate> '

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
        elif options['print']:
            line.append("print")
            line.append(options["<cert_id>"])
        elif options['export']:
            line.append("export")
            line.append(options["<cert_id>"])
        elif options['import']:
            line.append("import")
            line.append(options["<filename>"])
        return " ".join(line)

    @command()
    def do_list(self):
        """
        Usage: list
        """
        certs = self.cache._for_adf('certs')

        if len(certs):
            ui.print_certificates_header()
            for cert in sorted(certs.itervalues(), key=creation):
                aid = cert['signature'].aid
                title = cert['archive'].title
                size = archive_size(cert['archive'])
                ui.print_certificates_line( certificate={
                        'aid': aid,
                        'size':size,
                        'title': title,
                        'created':cert['archive'].meta.created
                    })
                if self.debug > 2:
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
            if self.batch:
                return
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
        path = self.cache.export_cert(cert_id)
        if path:
            print "Created file:"
            print path
        else:
            print "Certificate not found"

    @command(cert_id=str)
    def do_print(self, cert_id=None):
        """
        Usage: print <cert_id>
        """
        path = self.cache.print_cert(cert_id)
        if path:
            print "Created file:"
            print path
        else:
            print "Certificate not found"

    @command(filename=unicode)
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
                        self.cache.import_cert(filename)[0])
        else:
            print "No certificates found in", filename


class LaCapsuleCommand(LaBaseCommand):
    """Manage Long Access Capsules

    Usage: lacli capsule list
           lacli capsule create <title>
           lacli capsule --help

    """
    prompt = 'lacli:capsule> '

    def makecmd(self, options):
        line = []
        if options['list']:
            line.append("list")
        return " ".join(line)

    @login
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
                    print u"{:<10}:{:>10}".format(
                        'title', capsule.pop('title'))
                    for i, v in capsule.iteritems():
                        if i == 'resource_uri':
                            continue
                        print "{:<10}:{:>10}".format(i, v)
                    print "\n"
            else:
                print "No available capsules."
        except Exception as e:
            print "error: " + str(e)


class LaArchiveCommand(LaBaseCommand):
    """Upload a file to Long Access

    Usage: lacli archive upload [-n <np>] [<index>] [<capsule>]
           lacli archive list
           lacli archive status <index>
           lacli archive create <dirname> -t <title> [--desc <description>]
           lacli archive extract [-o <dirname>] <path> [<cert_id>|-f <cert>]
           lacli archive delete <index> [<srm>...]
           lacli archive --help

    Options:
        -n <np>, --procs <np>               number of processes [default: auto]
        -t <title>, --title <title>         title for prepared archive
        --desc <description>                description for prepared archive
        -o <dirname>, --out <dirname>       directory to restore archive
        -c <capsule>, --capsule <capsule>   capsule to upload to (see below)
        -f <cert>, --cert <cert>            certificate file to use
        -h, --help                          this help

    The archive will be uploaded to the first capsule that has enough available
    space.
    """
    prompt = 'lacli:archive> '

    def __init__(self, *args, **kwargs):
        super(LaArchiveCommand, self).__init__(*args, **kwargs)
        UploadState.init(self.cache)
        self.nprocs = None

    def setopt(self, options):
        try:
            if options['--procs'] != 'auto':
                self.nprocs = int(options['--procs'])
        except ValueError:
            print "error: illegal value for 'procs' parameter."
            raise

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
            line.append(quote(options['<dirname>']))
            if options['--title']:
                line.append(quote(options['--title']))
                if options['--desc']:
                    line.append(quote(options['--desc']))
        elif options['status']:
            line.append("status")
            line.append(options['<index>'])
        elif options['extract']:
            line.append("extract")
            line.append(quote(options['<path>']))
            if options['--out']:
                line.append(quote(options['--out']))
            else:
                line.append(quote(''))
            if options['--cert']:
                line.append("dummy")
                line.append(quote(options['--cert']))
            elif options['<cert_id>']:
                line.append(options['<cert_id>'])
        elif options['delete']:
            line.append("delete")
            line.append(options["<index>"])
            if options['<srm>']:
                line.append(quote(
                    " ".join(options["<srm>"])))
        return " ".join(line)

    @login
    @command(index=int, capsule=int)
    def do_upload(self, index=1, capsule=None):
        """
        Usage: upload [<index>] [<capsule>]
        """
        fname = None
        docs = list(self.cache._for_adf('archives').iteritems())
        docs = sorted(docs, key=compose(creation, operator.itemgetter(1)))

        _error = "Cannot upload: "

        if index <= 0 or len(docs) < index:
            _error += "no such archive."
        else:
            fname = docs[index-1][0]
            docs = docs[index-1][1]
            size = docs['archive'].meta.size

            capsules = self.session.capsule_ids()
            if capsule is not None:
                capsule = capsules.get(capsule)
                if not capsule:
                    _error += "no such capsule"
                elif capsule.get('remaining', 0) < size:
                    _error += "archive too big for capsule"
                    capsule = None
            elif len(capsules) > 0:
                for i, c in capsules.iteritems():
                    if c.get('remaining', 0) > size:
                        capsule = c
                if not capsule:
                    _error += "no capsules with available space found."
            else:
                _error += "no capsules found"

        if fname and capsule:
            link = docs['links']

            if link.upload or link.download:
                print "upload is already completed"
            else:
                try:
                    size = docs['archive'].meta.size
                    with UploadState.get(fname, size, capsule) as state:
                        signal.signal(signal.SIGINT, state.signal)

                        handler = ConsoleProgressHandler(
                            size=size, fname=fname, state=state)
                        with handler as progq:
                            saved = self.upload(docs, fname, progq, state)
                        if not self.batch:
                            print ""
                            print "Upload finished, waiting for verification"
                            print "Press Ctrl-C to check manually later"
                            status = self._poll_status(saved['link'])
                            if status['status'] == "error":
                                print "status: error"
                                self.cache.upload_error(fname)
                                state.error(True)
                            elif status['status'] == "completed":
                                print "status: completed"
                                UploadState.reset(fname)
                                fname = saved['fname']
                                cert, f = self.cache.save_cert(
                                    self.cache.upload_complete(fname, status))
                                if f:
                                    print "Certificate", cert, "saved:", f
                                else:
                                    print "Certificate", cert, "already exists"
                                print " ".join(("Use lacli certificate list",
                                                "to see your certificates, or",
                                                "lacli certificate --help for",
                                                "more options"))
                            else:
                                print "Unknown status received:", status['status']

                    print "\ndone."
                except Exception as e:
                    self.cache.upload_error(fname)
                    getLogger().debug("exception while uploading",
                                      exc_info=True)
                    print "error: " + str(e)
        else:
            print _error

    @defer.inlineCallbacks
    def _poll_status_async(self, link):
        u = yield self.session.upload_status_async(link)
        if u['status'] == "completed" or u['status'] == "error":
            defer.returnValue(u)
        else:
            yield task.deferLater(reactor, 5.0, _poll_status_async, link)

    @block
    def _poll_status(self, link):
        return self._poll_status_async(link)

    @defer.inlineCallbacks
    def upload_async(self, docs, fname, progq, state):
        archive = docs['archive']
        auth = docs['auth']
        path = self.cache.data_file(docs['links'])
        op = yield self.session.upload(state.capsule, archive, state)
        if op.uri is None:
            yield op.status  # init uri and status
            state.save_op(op)
        uploader = Upload(self.session, self.nprocs, self.debug, state)
        if state.progress < state.size:
            yield uploader.upload(path, op, progq)
        yield op.finalize(auth, state.keys)
        account = yield self.session.async_account
        saved = yield self.cache.save_upload(fname, docs, op.uri, account)
        defer.returnValue(saved)

    @block
    def upload(self, *args, **kwargs):
        return self.upload_async(*args, **kwargs)

    @command(directory=unicode, title=unicode, description=unicode)
    def do_create(self, directory=None, title="my archive", description=None):
        """
        Usage: create <directory> <title> [<description>]
        """
        try:
            if not os.path.isdir(directory):
                print "The specified folder does not exist."
                return

            def mycb(path, rel):
                if not path:
                    print "Encrypting.."
                else:
                    print path.encode('utf8'), "=>", rel.encode('utf8')
            self.cache.prepare(title, directory,
                               description=description, cb=mycb)
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
        archives = list(self.cache._for_adf('archives').iteritems())
        uploads = self.cache._get_uploads()

        if len(archives):
            ui.print_archives_header()
            bydate = sorted(archives, key=compose(creation, operator.itemgetter(1)))
            for n, docs in enumerate(bydate):
                fname = docs[0]
                archive = docs[1]
                status = "LOCAL"
                cert = ""
                if 'signature' in archive:
                    status = "COMPLETE"
                    cert = archive['signature'].aid
                elif 'links' in archive and archive['links'].upload:
                    status = "UPLOADED"
                    if self.verbose:
                        cert = archive['links'].upload
                elif fname in uploads:
                    status = "UPLOADING"
                title = archive['archive'].title
                size = archive_size(archive['archive'])
                ui.print_archives_line(archive = {
                        'num': n+1,
                        'size': size,
                        'title': title,
                        'status': status,
                        'cert':cert,
                        'created':archive['archive'].meta.created
                    })
                if self.debug > 2:
                    for doc in archive.itervalues():
                        pyaml.dump(doc, sys.stdout)
                    print
        else:
            print "No available archives."

    @login
    @command(index=int)
    def do_status(self, index=1):
        """
        Usage: status <index>
        """
        docs = list(self.cache._for_adf('archives').iteritems())
        docs = sorted(docs, key=compose(creation, operator.itemgetter(1)))
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
                    if status['status'] == "completed":
                        cert, f = self.cache.save_cert(
                            self.cache.upload_complete(fname, status))
                        if f:
                            print "Certificate", cert, "saved:", f
                        else:
                            print "Certificate", cert, "already exists.\n"
                        print " ".join(("Use lacli certificate list",
                                        "to see your certificates, or",
                                        "lacli certificate --help for",
                                        "more options"))
                    else:
                        print "upload not complete, status:", status['status']
                except Exception as e:
                    getLogger().debug("exception while checking status",
                                      exc_info=True)
                    print "error: " + str(e)

    @command(path=unicode, dest=unicode, cert_id=str, cert_file=unicode)
    def do_extract(self, path=None, dest=None, cert_id=None, cert_file=None):
        """
        Usage: extract <path> [<dest>] [<cert_id>] [<cert_file>]
        """
        if cert_file:
            certs = self.cache.certs([cert_file])
            cert_id = next(certs.iterkeys())
        else:
            certs = self.cache.certs()

        path = os.path.expanduser(path)
        if dest:
            dest = os.path.expanduser(dest)
        elif self.batch:
            dest = os.path.dirname(path)
        else:
            dest = os.getcwd()

        if not os.path.isfile(path):
            print "error: file", path, "does not exist"
        elif not os.path.isdir(dest):
            print "output directory", dest, "does not exist"
        else:
            try:
                if cert_id not in certs:
                    if len(certs) and not self.batch:
                        print "Select a certificate:"
                        while cert_id not in certs:
                            for n, cert in enumerate(certs.iteritems()):
                                cert = cert[1]
                                aid = cert['signature'].aid
                                title = cert['archive'].title
                                size = archive_size(cert['archive'])
                                print "{:>10} {:>6} {:<}".format(
                                    aid, size, title)
                            cert_id = raw_input("Enter a certificate ID: ")
                            assert cert_id, "No matching certificate found"
                    else:
                        print "No matching certificate found."

                def extract(cert, archive, dest=dest):
                    def _print(f):
                        print "Extracting", f
                    restore_archive(archive, path, cert,
                                    dest,
                                    self.cache._cache_dir(
                                        'tmp', write=True), _print)
                    print "archive restored."
                if cert_id in certs:
                    extract(certs[cert_id]['cert'], certs[cert_id]['archive'])
                else:
                    getLogger().debug("Key input gui unavailable and key not found",
                                          exc_info=True)
                    print "error: key not found"

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
        docs = sorted(docs, key=compose(creation, operator.itemgetter(1)))

        fname = path = None
        if index <= 0 or len(docs) < index:
            print "No such archive."
        else:
            fname = docs[index-1][0]
            docs = docs[index-1][1]
            archive = docs['archive']
            path = self.cache.data_file(docs['links'])

        srmprompt = "\n".join((
            "WARNING! Insecure deletion attempt.",
            "Could not find a secure deletion command",
            "The archive you are about to delete may still recoverable.",
            "For more information see: https://ssd.eff.org/tech/deletion"))
        fileprompt = "\n".join((
            "Please provide a valid srm command as an option or remove the",
            "file(s) manually:"))

        if not self.batch:
            print "Deleting archive", index, "({}) in 5".format(archive.title.encode('utf8')),
            for num in [4, 3, 2, 1]:
                sys.stdout.flush()
                time.sleep(1)
                sys.stdout.write(", {}".format(num))
            print "... deleting"

        self.cache.shred_archive(fname, srm)
        if os.path.exists(fname):
            if not srm:
                print srmprompt
            else:
                print srm, "failed."
            print fileprompt
            print fname
            if path:
                print path
        elif not os.path.exists(path):
            print "Deleted archive", archive.title,
            print " but local copy not found:", path
        else:
            self.cache.shred_file(path, srm)
            if os.path.exists(path):
                print "ERROR: Failed to delete archive data:", path
                print "Please remove manually"
            else:
                print "Deleted archive", archive.title
# vim: et:sw=4:ts=4
