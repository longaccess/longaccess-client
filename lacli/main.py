"""
Usage: lacli [--help] [-u <user>] [-p <pass>] [--verbose]
             [--home <home>] [--debug <level>] [--batch]
             <command> [<args>...]
       lacli -i

Commands (run lacli <command> -h for options):

    archive         manage archives
    capsule         manage capsules
    certificate     manage certificates
    login           configure access credentials
    server          run a RPC server

Options:
    -i, --interactive              interactive mode
    -u <user>, --user <user>       user name
    -p <pass>, --password <pass>   user password
    -d <level>, --debug <level>    debug level, from 0 to 2 [default: 0]
    --home <home>                  conf/cache dir [default: {home}]
    -v, --verbose                  print verbose information
    --batch                        be brief, don't ask questions
    -h, --help                     print this help
"""

import sys
import os
import cmd

from lacore.log import setupLogging, getLogger
from docopt import docopt, DocoptExit
from lacli.command import LaCapsuleCommand, LaCertsCommand, LaArchiveCommand
from lacli.login import LaLoginCommand
from lacli.server import LaServerCommand
from lacli import get_client_info, __version__
from lacore.api import RequestsFactory
from lacli.cache import Cache
from lacore.async import twisted_log_observer
from lacli.registry import LaRegistry
from datetime import datetime


default_home = os.path.expanduser(os.path.join('~', 'Longaccess'))


def settings(options):
    """
        >>> prefs, cache = settings({'--home': '/tmp', '--debug': 2})
        >>> cache.home
        '/tmp'
        >>> prefs['command']['debug']
        2
        >>> prefs['api']['verify']
        True
    """
    try:
        debug = int(options.get('--debug', 0))
    except ValueError:
        print "error: illegal value for 'debug' parameter."
        raise

    verify = True
    if '0' == os.getenv('LA_API_VERIFY'):
        verify = False

    batch = options.get('--batch')
    if not batch and os.getenv('LA_BATCH_OPERATION'):
        batch = True

    unsafe = False
    if '0' == os.getenv('LA_SAFE'):
        unsafe = True

    prefs = {
        'api': {
            'user': options.get('--user'),
            'pass': options.get('--password'),
            'url': os.getenv('LA_API_URL'),
            'verify': verify,
            'factory': RequestsFactory
        },
        'command': {
            'debug': debug,
            'verbose': options.get('--verbose'),
            'batch': batch,
            'unsafe': unsafe,
            'srm': None
        },
        'gui': {
            'rememberme': False,
            'username': None,
            'password': None,
            'email': None
        }
    }
    if options.get('<command>'):
        prefs[options['<command>']] = options.get('<args>')

    home = options.get('--home', default_home)
    if not home or not os.path.isdir(home):
        if not batch:
            while not home or not os.path.isdir(home):
                if not home:
                    print "Enter directory for Longaccess data? [{}]: ".format(
                        default_home)
                    home = sys.stdin.readline().strip() or default_home
                elif os.path.isfile(home):
                    print "{} is not a directory.".format(home)
                    print "Enter directory for Longaccess data? : "
                    home = sys.stdin.readline().strip()
                else:
                    print home, "does not exist."
                    print "Should I create it? (yes/no): "
                    if sys.stdin.readline().strip().lower() != 'yes':
                        sys.exit('Unable to proceed without home directory')
                os.makedirs(home)

    cache = Cache(None)
    try:
        if not os.path.isdir(home):
            os.makedirs(home)
        cache = Cache(home)
        prefs = cache.merge_prefs(prefs)
    except Exception:
        if debug > 0:
            getLogger().exception("initialization exception")

    return (prefs, cache)


class LaCommand(cmd.Cmd):
    prompt = 'lacli> '
    archive = None
    capsule = None
    certificate = None
    login = None

    def __init__(self, cache, prefs):
        cmd.Cmd.__init__(self)
        registry = LaRegistry(cache, prefs, self)
        self.archive = LaArchiveCommand(registry)
        self.capsule = LaCapsuleCommand(registry)
        self.certificate = LaCertsCommand(registry)
        self.login = LaLoginCommand(registry)
        self.server = LaServerCommand(registry)

    def do_EOF(self, line):
        print
        return True

    def dispatch(self, subcmd, options):
        options.insert(0, subcmd)
        try:
            subcmd = getattr(self, subcmd)
        except AttributeError:
            print "Unrecognized command:", subcmd
            print(__doc__)
            return
        try:
            line = subcmd.makecmd(docopt(subcmd.__doc__, options))
        except DocoptExit as e:
            print e
            return
        self.dispatch_one(subcmd, line)

    def dispatch_one(self, subcmd, line, interactive=False):
        try:
            if line:
                subcmd.onecmd(line)
            elif interactive:
                subcmd.cmdloop()
        except Exception as e:
            getLogger().debug("command returned error", exc_info=True)
            print "error:", str(e)

    def do_archive(self, line):
        self.dispatch_one(self.archive, line, True)

    def do_capsule(self, line):
        self.dispatch_one(self.capsule, line, True)

    def do_certificate(self, line):
        self.dispatch_one(self.certificate, line, True)

    def do_login(self, line):
        self.login.onecmd('login ' + line)

    def do_server(self, line):
        self.server.onecmd('server ' + line)


def main(args=sys.argv[1:]):
    """Main function called by `lacli` command.
    """
    options = docopt(__doc__.format(home=default_home),
                     version='lacli {}'.format(__version__),
                     options_first=True)
    prefs, cache = settings(options)
    level = prefs['command']['debug']
    with setupLogging(level=level, logfile=cache.log):
        with twisted_log_observer(level):
            getLogger().debug("{} starting on {}".format(
                get_client_info(), datetime.now().isoformat()))
            cli = LaCommand(cache, prefs)
            if options['<command>']:
                cli.dispatch(options['<command>'], options['<args>'])
            elif options['--interactive']:
                cli.cmdloop()

if __name__ == "__main__":
    main()
