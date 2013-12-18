from lacli.decorators import command
from lacli.log import getLogger
from lacli.command import LaBaseCommand
from lacli.decorators import contains, login
from twisted.python.log import startLogging, msg, err
from twisted.internet import reactor
from thrift.transport import TTwisted
from thrift.protocol import TBinaryProtocol
from lacli.server.interface.ClientInterface import CLI, ttypes
from lacli.server.error import tthrow
from itertools import starmap
from lacli.progress import BaseProgressHandler
import sys
import os


class ServerProgressHandler(BaseProgressHandler):
    def update(self, progress):
        msg('Progress: ' + progress)
        

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

    def toArchive(self, fname, docs):
        created = docs['archive'].meta.created
        size = docs['archive'].meta.size
        title = docs['archive'].title
        description = docs['archive'].description
        md5 = docs['auth'].md5.encode('hex')
        status = self.cache.archive_status(docs)
        ident = os.path.basename(fname)
        if title is not None:
            title = title.encode('utf8')
        if description is not None:
            description = description.encode('utf8')
        return ttypes.Archive(
            ident,
            status,
            ttypes.ArchiveInfo(
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
                md5))

    def PingCLI(self):
        msg('pingCLI()')
        return True

    @tthrow
    def LoginUser(self, username, password, remember):
        self.logincmd.login_batch(username, password)
        if remember:
            msg('Saving credentials for <'+self.logincmd.email+'>')
            self.registry.save_session(
                self.logincmd.username, self.logincmd.password)
        return True

    @tthrow
    def Logout(self):
        self.logincmd.logout_batch()
        return True

    @contains(list)
    def capsules(self):
        cs = self.session.capsules()
        for c in cs:
            yield ttypes.Capsule(
                '', str(c['id']), c['resource_uri'],
                c['title'], '', ttypes.DateInfo(),
                c['size'], c['remaining'], [])

    @tthrow
    @login
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

        fname, docs = self.cache.prepare(
            "_temp", paths, description="_temp", cb=progress)

        return self.toArchive(fname, docs)

    @tthrow
    def GetUploads(self):
        """
          list<Archive> GetUploads(),
        """
        archives = self.cache._for_adf('archives')
        return list(starmap(self.toArchive, archives.iteritems()))

    @tthrow
    @login
    def UploadToCapsule(self, archive, capsule, title, description):
        """
          void UploadToCapsule(1: string ArchiveLocalID, 2: string CapsuleID,
            3: string title, 4: string description)
        """
        docs = self.cache.get_adf(archive)
        status = self.cache.archive_status(docs)
        if status != ttypes.ArchiveStatus.Local:
            raise ValueError("Archive state invalid")

        capsule = self.session.capsule_ids().get(int(capsule))
        if capsule is None:
            raise ValueError("Capsule not found")

        if capsule.get('remaining', 0) < docs['archive'].meta.size:
            raise ValueError("Capsule is not big enough")

        with ServerProgressHandler(docs['archive'].meta.size) as progq:
            self.registry.cmd.archive.upload(
                capsule, docs, archive, progq)

    @tthrow
    def ResumeUpload(self, archive):
        """
          void ResumeUpload(1: string ArchiveLocalID)
        """
        raise NotImplementedError("not implemented")

    @tthrow
    def QueryArchiveStatus(self, archive):
        """
          TransferStatus QueryArchiveStatus(1: string ArchiveLocalID)
        """
        raise NotImplementedError("not implemented")

    @tthrow
    def PauseUpload(self, archive):
        """
          void PauseUpload(1: string ArchiveLocalID)
        """
        raise NotImplementedError("not implemented")

    @tthrow
    @login
    def CancelUpload(self, archive):
        """
          void CancelUpload(1: string ArchiveLocalID)
        """
        raise NotImplementedError("not implemented")

    @tthrow
    def GetCertificates(self):
        """
          list<Certificate> getCertificates(),
        """
        raise NotImplementedError("not implemented")

    @tthrow
    def GetCertificateFolder(self):
        """
          string GetCertificateFolder(),
        """
        raise NotImplementedError("not implemented")

    @tthrow
    def GetArchivesFolder(self):
        """
          string GetarchivesFolder(),
        """
        raise NotImplementedError("not implemented")

    @tthrow
    def SetCertificateFolder(self, path):
        """
          void SetCertificateFolder(1: string path),
        """
        raise NotImplementedError("not implemented")

    @tthrow
    def ExportCertificate(self, archive, fmt):
        """
          binary ExportCertificate(1: string ArchiveID,
            2: CertExportFormat format)
        """
        raise NotImplementedError("not implemented")

    @tthrow
    def GetDefaultExtractionPath(self):
        """
          string GetDefaultExtractionPath(),
        """
        raise NotImplementedError("not implemented")

    @tthrow
    def Decrypt(self, path, key, dest):
        """
          void Decrypt(1: string archivePath,2: string key,
            3: string destinationPath)
        """
        raise NotImplementedError("not implemented")
