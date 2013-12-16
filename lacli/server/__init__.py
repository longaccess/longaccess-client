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
import sys


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
          Archive CreateArchive(1: list<string> filePaths)
        """
        raise NotImplementedError("not implemented")

    @tthrow
    def GetUploads(self):
        """
          list<Archive> GetUploads(),
        """
        raise NotImplementedError("not implemented")

    @tthrow
    @login
    def UploadToCapsule(self, archive, capsule, title, description):
        """
          void UploadToCapsule(1: string ArchiveLocalID, 2: string CapsuleID,
            3: string title, 4: string description)
        """
        raise NotImplementedError("not implemented")

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
