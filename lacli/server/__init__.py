from lacli import __version__
from lacli.log import getLogger
from lacli.adf import make_adf, Archive, Certificate, Meta, Cipher
from lacli.archive import restore_archive
from lacli.basecmd import LaBaseCommand
from lacli.command import command
from lacli.loginutil import login_async
from lacli.decorators import expand_args
from lacli.exceptions import UploadError
from twisted.python.log import msg, err, PythonLoggingObserver
from twisted.internet import reactor, defer, threads, task
from thrift.transport import TTwisted
from thrift.protocol import TBinaryProtocol
from lacli.server.interface.ClientInterface import CLI, ttypes
from lacli.server.error import tthrow, log_hide
from itertools import starmap
from lacli.progress import ServerProgressHandler
from lacli.upload import UploadState
from binascii import b2a_hex
from StringIO import StringIO
import os
import errno
import treq
import json


class LaServerCommand(LaBaseCommand, CLI.Processor):
    """Run a RPC server

    Usage: lacli server [--no-detach] [--port <port>] [--mhole]

    Options:
        --no-detach              don't detach from terminal
        --port <port>            port to listen on [default: 9090]
        --mhole                  start a manhole on the next port number
    """
    prompt = 'lacli:server> '

    def __init__(self, *args, **kwargs):
        super(LaServerCommand, self).__init__(*args, **kwargs)
        self.logincmd = self.registry.cmd.login
        self.manhole = False
        self.srm = self.prefs['command']['srm']
        if self.prefs['gui']['rememberme'] is True:
            self.logincmd.username = self.prefs['gui']['username']
            self.logincmd.password = self.prefs['gui']['password']
        UploadState.init(self.cache)
        CLI.Processor.__init__(self, self)

    def makecmd(self, options):
        cmd = ["run"]
        if options['--port']:
            cmd.append(options['--port'])
        if options['--mhole']:
            self.manhole = True
        return " ".join(cmd)

    def get_server(self):
        factory = TBinaryProtocol.TBinaryProtocolFactory()
        return TTwisted.ThriftServerFactory(
            processor=self, iprot_factory=factory)

    @command(port=int)
    def do_run(self, port=9090):
        """
        Usage: run [<port>]
        """
        reactor.listenTCP(port, self.get_server(), interface='127.0.0.1')
        if self.manhole is True:
            from twisted.manhole.telnet import ShellFactory
            f = ShellFactory()
            f.username = f.password = 'admin'
            reactor.listenTCP(port+1, f)
        tlog = PythonLoggingObserver()
        tlog.start()
        msg('Running reactor')
        self.batch = True
        if self.prefs['gui']['rememberme'] is True:
            self.logincmd.username = self.prefs['gui']['username']
            self.logincmd.password = self.prefs['gui']['password']
            self.logincmd.email = self.prefs['gui']['email']
        reactor.run()
        self.batch = False
        tlog.stop()

    def process(self, iprot, oprot):
        d = CLI.Processor.process(self, iprot, oprot)
        d.addErrback(self.logUnhandledError)
        return d

    def logUnhandledError(self, error):
        err(error)
        getLogger().debug("unhandled error: ", exc_info=True)
        return error

    def toArchiveInfo(self, docs):
        title = docs['archive'].title
        size = docs['archive'].meta.size
        created = docs['archive'].meta.created
        description = docs['archive'].description
        md5 = docs['auth'].md5.encode('hex')
        if title is not None:
            title = title.encode('utf8')
        if description is not None:
            description = description.encode('utf8')
        return ttypes.ArchiveInfo(
            title,
            description,
            size,
            ttypes.DateInfo(
                created.day,
                created.month,
                created.year,
                created.hour,
                created.minute,
                created.second),
            md5)

    def toArchive(self, fname, docs):
        status = self.cache.archive_status(fname, docs)
        ident = os.path.basename(fname)
        return ttypes.Archive(
            ident,
            status,
            self.toArchiveInfo(docs))

    def PingCLI(self):
        msg('pingCLI()')
        return True

    @tthrow
    def UserIsLoggedIn(self):
        if self.session is None:
            return False
        if self.logincmd.email is None:
            if self.logincmd.username is not None:
                try:
                    d = self.logincmd.login_async(
                        self.logincmd.username, self.logincmd.password)
                    d.addCallback(lambda x: True)
                    d.addErrback(lambda x: False)
                    return d
                except Exception:
                    getLogger().debug("Couldn't login", exc_info=True)
            return False
        else:
            return True

    @tthrow
    @log_hide(_args=True)
    @defer.inlineCallbacks
    def LoginUser(self, username, password, remember):
        yield self.logincmd.login_async(username, password)
        if remember:
            getLogger().debug("Saving credentials for {}".format(
                self.logincmd.username))
            self.prefs['gui']['username'] = self.logincmd.username
            self.prefs['gui']['password'] = self.logincmd.password
            self.prefs['gui']['rememberme'] = remember
            self.cache.save_prefs(self.prefs)
        defer.returnValue(True)

    @tthrow
    def Logout(self):
        self.logincmd.logout_batch()
        if self.prefs['gui']['rememberme'] is True:
            # clear credentials
            self.prefs['gui']['username'] = None
            self.prefs['gui']['password'] = None
            self.prefs['gui']['rememberme'] = False
            self.cache.save_prefs(self.prefs)
        return True

    @defer.inlineCallbacks
    def capsules(self):
        cs = yield self.session.async_capsules()
        defer.returnValue([
            ttypes.Capsule(
                '', str(c['id']), c['resource_uri'],
                c['title'], '', ttypes.DateInfo(),
                c['size'], c['remaining'], [])
            for c in cs])

    @tthrow
    @login_async
    def GetCapsules(self):
        """
        """
        return self.capsules()

    @tthrow
    def CreateArchive(self, paths):
        """
        """
        paths = map(lambda p: p.decode('utf-8'), paths)

        def progress(path, rel):
            if not path:
                msg("Encrypting..")
            else:
                msg(rel.encode('utf8'))

        args = ["_temp", paths]
        kwargs = {'description': "_temp", 'cb': progress}
        d = threads.deferToThread(self.cache.prepare, *args, **kwargs)
        d.addCallback(expand_args(self.toArchive))
        return d

    @tthrow
    def GetUploads(self):
        """
          list<Archive> GetUploads(),
        """
        archives = self.cache._for_adf('archives')
        return list(starmap(self.toArchive, archives.iteritems()))

    def reset_upload(self, archive, times=3):
        try:
            return UploadState.reset(archive)
        except OSError as e:
            if e.errno == errno.EACCES and times > 0:
                args = [self.reset_upload, archive, times-1]
                return task.deferLater(reactor, 2, *args)
            raise

    @defer.inlineCallbacks
    def _upload(self, f, d, s):
        size = d['archive'].meta.size
        acmd = self.registry.cmd.archive
        with s:
            with ServerProgressHandler(maxval=size, state=s) as progq:
                with self.cache._archive_open(f, 'w') as _archive:
                    make_adf(list(d.itervalues()), out=_archive)
                saved = yield acmd.upload_async(d, f, progq, s)
            status = yield acmd._poll_status_async(saved['link'])
            while status is None:
                getLogger().debug("couldn't get status, "
                                  "retrying..")
                status = yield acmd._poll_status_async(saved['link'])
            getLogger().debug("API returned status: {}".format(status))
            if status['status'] == "error":
                raise UploadError()
            elif status['status'] == "completed":
                fname = saved['fname']
                getLogger().debug("upload completed")
                self.cache.save_cert(self.cache.upload_complete(fname, status))
                self.reset_upload(f)

    @tthrow
    @login_async
    @defer.inlineCallbacks
    def UploadToCapsule(self, archive, capsule, title, description):
        """
          void UploadToCapsule(1: string ArchiveLocalID, 2: string CapsuleID,
            3: string title, 4: string description)
        """
        docs = self.cache.get_adf(archive)
        docs['archive'].title = title
        docs['archive'].description = description
        status = self.cache.archive_status(archive, docs)
        if status != ttypes.ArchiveStatus.Local:
            raise ValueError("Archive state invalid")
        size = docs['archive'].meta.size
        cs = yield self.session.async_capsules()
        for c in cs:
            if c['id'] == int(capsule):
                if c.get('remaining', 0) >= docs['archive'].meta.size:
                    capsule = c
                    break
                else:
                    raise ValueError("Capsule is not big enough")
        else:
            raise ValueError("Capsule not found")

        state = UploadState.get(archive, size, capsule)
        if state.exc is not None:
            raise ValueError("Archive has error")

        self._upload(archive, docs, state)

    @tthrow
    @login_async
    def ResumeUpload(self, archive):
        """
          void ResumeUpload(1: string ArchiveLocalID)
        """
        docs = self.cache.get_adf(archive)
        status = self.cache.archive_status(archive, docs)
        if status == ttypes.ArchiveStatus.Completed:
            raise ValueError("Archive already complete")
        if status == ttypes.ArchiveStatus.Local:
            raise ValueError("Archive upload has not started yet.")
        state = UploadState.get(archive)
        self._upload(archive, docs, state)

    @tthrow
    def QueryArchiveStatus(self, archive):
        """
          TransferStatus QueryArchiveStatus(1: string ArchiveLocalID)
        """
        docs = self.cache.get_adf(archive)
        status = self.cache.archive_status(archive, docs)
        eta = description = ''
        remaining = progress = 0

        getLogger().debug("cached status: {}".format(status))
        if status == ttypes.ArchiveStatus.Completed:
            progress = docs['archive'].meta.size
        elif UploadState.has_state(archive):
            state = UploadState.get(archive)
            if state.exc is not None:
                status = ttypes.ArchiveStatus.Failed
            if state.active():
                status = ttypes.ArchiveStatus.InProgress
            getLogger().debug("state status: {}".format(status))
            progress = state.progress
            remaining = state.size - progress
            if state in ServerProgressHandler.uploads:
                elapsed = ServerProgressHandler.uploads[state].seconds_elapsed
                if progress > 0:
                    eta = str(int(elapsed * state.size / progress - elapsed))
        else:
            remaining = docs['archive'].meta.size
        return ttypes.TransferStatus(
            description, eta, remaining, progress, status)

    @tthrow
    def PauseUpload(self, archive):
        """
          void PauseUpload(1: string ArchiveLocalID)
        """
        if not UploadState.has_state(archive):
            raise ValueError("archive not found")
        UploadState.states[archive].pause()

    @login_async
    def _delete_upload(self, archive):
        if UploadState.has_state(archive):
            UploadState.states[archive].pause()
            self.reset_upload(archive)

    def _delete_archive(self, archive):
        self._delete_upload(archive)
        docs = self.cache.get_adf(archive)
        fname = self.cache.shred_archive(archive, self.srm, True)
        assert not os.path.exists(fname), fname + " still exists!"
        path = self.cache.data_file(docs['links'])
        self.cache.shred_file(path, self.srm, True)

    @tthrow
    def CancelUpload(self, archive):
        """
          void CancelUpload(1: string ArchiveLocalID)
        """
        return threads.deferToThread(self._delete_archive, archive)

    def toSignature(self, docs):
        sig = docs['signature']
        return ttypes.Signature(
            sig.aid,
            ttypes.DateInfo(
                sig.created.day,
                sig.created.month,
                sig.created.year,
                sig.created.hour,
                sig.created.minute,
                sig.created.second),
            sig.creator,
            "")

    def toCertificate(self, ident, docs):
        return ttypes.Certificate(
            b2a_hex(docs['cert'].key).upper(),
            self.toSignature(docs),
            self.toArchiveInfo(docs),
            ident)

    @tthrow
    def GetCertificates(self):
        """
          list<Certificate> getCertificates(),
        """
        certs = self.cache._for_adf('certs')
        return list(starmap(self.toCertificate, certs.iteritems()))

    @tthrow
    @log_hide(_ret=True)
    def ExportCertificate(self, archive, fmt):
        """
          binary ExportCertificate(1: string ArchiveID,
            2: CertExportFormat format)
        """
        docs = self.cache.get_adf(archive, 'certs')
        out = StringIO()
        if fmt == ttypes.CertExportFormat.PDF:
            raise NotImplementedError("not implemented")
        elif fmt == ttypes.CertExportFormat.YAML:
            make_adf(list(docs.itervalues()), out=out, pretty=True)
            return out.getvalue()
        elif fmt == ttypes.CertExportFormat.HTML:
            out.write(self.cache._printable_cert(docs))
            return out.getvalue()
        else:
            raise NotImplementedError("Unknown format")

    @tthrow
    @log_hide(_args=True)
    def Decrypt(self, path, key, dest):
        """
          void Decrypt(1: string archivePath,2: string key,
            3: string destinationPath)
        """
        cert = Certificate(key.decode('hex'))
        archive = Archive("_temp", Meta('zip', Cipher('aes-256-ctr', 1)),
                          description="_temp")

        def _print(f):
            msg("Extracting {}".format(f))
        return threads.deferToThread(
            restore_archive, archive, path, cert, dest,
            self.cache._cache_dir('tmp', write=True), _print)

    @tthrow
    def CloseWhenPossible(self):
        reactor.callLater(1, reactor.stop)

    @tthrow
    @log_hide(_ret=True)
    def GetSettings(self):
        return ttypes.Settings(
            self.prefs['gui']['username'] or "",
            self.prefs['gui']['password'] or "",
            self.prefs['gui']['rememberme'],
            self.cache._cache_dir('archives'),
            self.cache._cache_dir('certs'))

    @tthrow
    @log_hide(_ret=True)
    def SetSettings(self, settings):
        if self.logincmd.email == self.logincmd.username:
            if settings.StoredUserName != self.logincmd.username:
                self.logincmd.email = settings.StoredUserName
        self.logincmd.username = settings.StoredUserName
        self.logincmd.password = settings.StoredPassword
        self.prefs['gui']['rememberme'] = settings.RememberMe
        self.prefs['gui']['username'] = settings.StoredUserName
        self.prefs['gui']['password'] = settings.StoredPassword
        self.cache.save_prefs(self.prefs)
        # TODO handle folder settings

    @tthrow
    @defer.inlineCallbacks
    def GetLatestVersion(self):
        try:
            r = yield treq.get("http://download.longaccess.com/latest.json")
            if r.code != 200:
                raise Exception("error getting latest version: {} {}".format(
                    r.code, r.phrase))
            r = yield treq.content(r)
            vinfo = {k: v for k, v in json.loads(r).iteritems()
                     if k in ("version", "description", "uri")}
        except Exception:
            getLogger().debug("couldn't get latest version", exc_info=True)
            vinfo = {"version": __version__}
        defer.returnValue(ttypes.VersionInfo(**vinfo))

    @tthrow
    def GetVersion(self):
        return ttypes.VersionInfo(version=__version__)

# vim: et:sw=4:ts=4
