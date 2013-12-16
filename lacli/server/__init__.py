from lacli.decorators import command
from lacli.log import getLogger
from lacli.command import LaBaseCommand
from lacli.exceptions import ApiAuthException
from lacli.decorators import contains
from twisted.python.log import startLogging, msg, err
from twisted.internet import reactor
from thrift.transport import TTwisted
from thrift.protocol import TBinaryProtocol
from lacli.server.interface.ClientInterface import CLI
from lacli.server.interface.ClientInterface.ttypes import InvalidOperation
from lacli.server.interface.ClientInterface.ttypes import ErrorType, Capsule, DateInfo
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

    def LoginUser(self, username, password, remember):
        try:
            email = self.logincmd.login_batch(username, password)
            msg("LoginUser() => {}".format(email))
            if remember:
                self.registry.save_session(
                    self.logincmd.username, self.logincmd.password)
        except Exception as e:
            err(e)
            raise InvalidOperation(
                ErrorType.Authentication, "Authentication failed")
        return True

    def Logout(self):
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    @contains(list)
    def capsules(self):
        cs = self.session.capsules()
        for c in cs:
            yield Capsule('', str(c['id']), c['resource_uri'],
                          c['title'], '', DateInfo(),
                          c['size'], c['remaining'], [])

    def GetCapsules(self):
        """
          list<Capsule> GetCapsules() throws (1:InvalidOperation error),
        """
        try:
            return self.capsules()
        except ApiAuthException as e:
            raise InvalidOperation(ErrorType.Authentication, e.msg)

    def CreateArchive(self, paths):
        """
          Archive CreateArchive(1: list<string> filePaths)
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def GetUploads(self):
        """
          list<Archive> GetUploads(),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def UploadToCapsule(self, archive, capsule, title, description):
        """
          void UploadToCapsule(1: string ArchiveLocalID, 2: string CapsuleID,
            3: string title, 4: string description)
            throws (1:InvalidOperation error),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def ResumeUpload(self, archive):
        """
          void ResumeUpload(1: string ArchiveLocalID)
            throws (1:InvalidOperation error),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def QueryArchiveStatus(self, archive):
        """
          TransferStatus QueryArchiveStatus(1: string ArchiveLocalID)
            throws (1:InvalidOperation error),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def PauseUpload(self, archive):
        """
          void PauseUpload(1: string ArchiveLocalID)
            throws (1:InvalidOperation error),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def CancelUpload(self, archive):
        """
          void CancelUpload(1: string ArchiveLocalID)
            throws (1:InvalidOperation error),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def GetCertificates(self):
        """
          list<Certificate> getCertificates(),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def GetCertificateFolder(self):
        """
          string GetCertificateFolder(),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def GetArchivesFolder(self):
        """
          string GetarchivesFolder(),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def SetCertificateFolder(self, path):
        """
          void SetCertificateFolder(1: string path),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def ExportCertificate(self, archive, fmt):
        """
          binary ExportCertificate(1: string ArchiveID,
            2: CertExportFormat format)
            throws (1:InvalidOperation error),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def GetDefaultExtractionPath(self):
        """
          string GetDefaultExtractionPath(),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def Decrypt(self, path, key, dest):
        """
          void Decrypt(1: string archivePath,2: string key,
            3: string destinationPath)
            throws (1:InvalidOperation error)
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")
