from lacli.decorators import command
from lacli.command import LaBaseCommand
from twisted.python.log import startLogging, msg
from twisted.internet import reactor
from thrift.transport import TTwisted
from thrift.protocol import TBinaryProtocol
from lacli.server.interface.ClientInterface import CLI

import sys
import zope


class LaServerCommand(LaBaseCommand):
    """Run a RPC server

    Usage: lacli server [--no-detach] [--port <port>]

    Options:
        --no-detach              don't detach from terminal
        --port <port>            port to listen on [default: 9090]
    """
    zope.interface.implements(CLI.Iface)
    prompt = 'lacli:server> '

    def makecmd(self, options):
        cmd = ["run"]
        if options['--port']:
            cmd.append(options['--port'])
        return " ".join(cmd)

    @command(port=int)
    def do_run(self, port=9090):
        """
        Usage: run [<port>]
        """
        reactor.listenTCP(port, TTwisted.ThriftServerFactory(
            processor=CLI.Processor(self),
            iprot_factory=TBinaryProtocol.TBinaryProtocolFactory()))
        startLogging(sys.stderr)
        msg('Running reactor')
        reactor.run()

    def PingCLI(self):
        msg('pingCLI()')
