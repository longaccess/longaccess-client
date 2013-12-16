from lacli.decorators import command
from lacli.command import LaBaseCommand
from twisted.python.log import startLogging, msg, err
from twisted.internet import reactor
from thrift.transport import TTwisted
from thrift.protocol import TBinaryProtocol
from lacli.server.interface.ClientInterface import CLI
from lacli.server.interface.ClientInterface.ttypes import InvalidOperation
from lacli.server.interface.ClientInterface.ttypes import ErrorType
import sys


class LaServerProcessor(CLI.Processor):

    def __init__(self, *args, **kwargs):
        CLI.Processor.__init__(self, self)

    def process(self, iprot, oprot):
        d = CLI.Processor.process(self, iprot, oprot)
        d.addErrback(self.logUnhandledError)
        return d

    def logUnhandledError(self, error):
        err(error)
        return error

    def PingCLI(self):
        msg('pingCLI()')
        return True

    def LoginUser(self, username, password, remember):
        msg('LoginUser({}, {}, {})'.format(username, password, remember))
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def Logout(self):
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

    def GetCapsules(self):
        """
          list<Capsule> GetCapsules() throws (1:InvalidOperation error),
        """
        raise InvalidOperation(ErrorType.NotImplemented, "not implemented")

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


class LaServerCommand(LaBaseCommand):
    """Run a RPC server

    Usage: lacli server [--no-detach] [--port <port>]

    Options:
        --no-detach              don't detach from terminal
        --port <port>            port to listen on [default: 9090]
    """
    prompt = 'lacli:server> '

    def makecmd(self, options):
        cmd = ["run"]
        if options['--port']:
            cmd.append(options['--port'])
        return " ".join(cmd)

    def get_server(self):
        processor = LaServerProcessor()
        factory = TBinaryProtocol.TBinaryProtocolFactory()
        return TTwisted.ThriftServerFactory(
            processor=processor, iprot_factory=factory)

    @command(port=int)
    def do_run(self, port=9090):
        """
        Usage: run [<port>]
        """
        reactor.listenTCP(port, self.get_server())
        startLogging(sys.stderr)
        msg('Running reactor')
        reactor.run()
