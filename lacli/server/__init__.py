from lacli.decorators import command
from lacli.log import getLogger
from lacli.compose import compose
from lacli.adf import make_adf, Archive, Certificate, Meta, Cipher
from lacli.archive import restore_archive
from lacli.command import LaBaseCommand
from lacli.decorators import contains, login_async, expand_args
from lacli.exceptions import PauseEvent
from twisted.python.log import startLogging, msg, err
from twisted.internet import reactor, defer, threads, task
from thrift.transport import TTwisted
from thrift.protocol import TBinaryProtocol
from lacli.server.interface.ClientInterface import CLI, ttypes
from lacli.server.error import tthrow
from itertools import starmap
from lacli.progress import ServerProgressHandler
from lacli.upload import UploadState
from binascii import b2a_hex
from StringIO import StringIO
import sys
import os
import errno


class LaServerCommand(LaBaseCommand, CLI.Processor):
    """Run a RPC server

    Usage: lacli server [--no-detach] [--port <port>]

    Options:
        --no-detach              don't detach from terminal
        --port <port>            port to listen on [default: 9090]
    """
    prompt = 'lacli:server> '

    def __init__(self, *args, **kwargs):
        super(LaServerCommand, self).__init__(*args, **kwargs)
        self.logincmd = self.registry.cmd.login
        UploadState.init(self.cache)
        CLI.Processor.__init__(self, self)

    def makecmd(self, options):
        cmd = ["run"]
        if options['--port']:
            cmd.append(options['--port'])
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
        reactor.listenTCP(port, self.get_server())
        startLogging(sys.stderr)
        msg('Running reactor')
        self.batch = True
        reactor.run()
        self.batch = False

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
        d = defer.Deferred()
        reactor.callLater(1, d.callback, True)
        return d


    @tthrow
    def UserIsLoggedIn(self):
        if self.session is None or self.registry.cmd.login.email is None:
            return False
        return True
        

    @tthrow
    @defer.inlineCallbacks
    def LoginUser(self, username, password, remember):
        if self.session is None or self.registry.cmd.login.email is None:
            yield self.logincmd.login_async(username, password)
            if remember:
                self.registry.save_session(
                    self.logincmd.username, self.logincmd.password)
        defer.returnValue(True)

    @tthrow
    def Logout(self):
        self.logincmd.logout_batch()
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
        def progress(path, rel):
            if not path:
                msg("Encrypting..")
            else:
                msg(rel.encode('utf8'))

        d = threads.deferToThread(self.cache.prepare,
            "_temp", paths, description="_temp", cb=progress)
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
                return task.deferLater(reactor, 2,
                    self.reset_upload, archive, times-1)
            raise

    @defer.inlineCallbacks
    def _upload(self, f, d, s):
        size = d['archive'].meta.size
        acmd = self.registry.cmd.archive
        with s:
            try:
                with ServerProgressHandler(size=size, state=s) as progq:
                    saved = yield acmd.upload_async(d, f, progq, s)
                status = yield acmd._poll_status_async(saved['link'])
            except PauseEvent as e:
                getLogger().debug("upload paused.")
                return
            except Exception as e:
                getLogger().debug("error in upload", exc_info=True)
                s.error(e)
                return
            if status['status'] == "error":
                getLogger().debug("upload error")
                s.error(True)
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
    def ResumeUpload(self, archive):
        """
          void ResumeUpload(1: string ArchiveLocalID)
        """
        docs = self.cache.get_adf(archive)
        status = self.cache.archive_status(archive, docs)
        if status != ttypes.ArchiveStatus.InProgress:
            raise ValueError("Archive state invalid")
        state = UploadState.get(archive)
        if state.exc is not None:
            raise ValueError("Archive has error")

        self._upload(archive, docs, state)

    def toTransferStatus(self, state):
        return ttypes.TransferStatus(
            'description',
            'eta',
            state.size - state.progress,
            state.progress)

    @tthrow
    def QueryArchiveStatus(self, archive):
        """
          TransferStatus QueryArchiveStatus(1: string ArchiveLocalID)
        """
        docs = self.cache.get_adf(archive)
        status = self.cache.archive_status(archive, docs)
        if status == ttypes.ArchiveStatus.Completed:
            return ttypes.TransferStatus(
                'description',
                'eta',
                0, 
                docs['archive'].meta.size)
        if status == ttypes.ArchiveStatus.InProgress:
            if archive not in UploadState.states:
                raise ValueError("archive not found")
            return self.toTransferStatus(UploadState.states[archive])
        raise ValueError("Archive state invalid")

    @tthrow
    def PauseUpload(self, archive):
        """
          void PauseUpload(1: string ArchiveLocalID)
        """
        if archive not in UploadState.states:
            raise ValueError("archive not found")
        UploadState.states[archive].pause()

    @tthrow
    @login_async
    def CancelUpload(self, archive):
        """
          void CancelUpload(1: string ArchiveLocalID)
        """
        if archive in UploadState.states:
            UploadState.states[archive].pause()
        self.reset_upload(archive)

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
    def GetSettings(self):
        return ttypes.Settings(
            self.registry.cmd.login.username or "",
            self.registry.cmd.login.password or "",
            False,
            self.cache._cache_dir('archives'),
            self.cache._cache_dir('certs'))

    @tthrow
    def SetSettings(self, settings):
        self.registry.cmd.login.username = settings.StoredUserName
        self.registry.cmd.login.password = settings.StoredPassword
        # TODO handle rememberme and folder settings

# vim: et:sw=4:ts=4
