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

from lacli.log import setupLogging
from docopt import docopt, DocoptExit
from lacli.command import LaCapsuleCommand, LaCertsCommand, LaArchiveCommand
from lacli.login import LaLoginCommand
from lacli import __version__
from lacli.api import RequestsFactory
from lacli.cache import Cache
from lacli.registry import LaRegistry


default_home = os.path.join('~', 'Longaccess')


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
            'batch': batch
        },
    }
    if options.get('<command>'):
        prefs[options['<command>']] = options.get('<args>')

    home = options.get('--home', default_home)
    if not home or not os.path.isdir(os.path.expanduser(home)):
        if batch:
            sys.exit("{} does not exist!".format(home))
        else:
            while not home or not os.path.isdir(os.path.expanduser(home)):
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
                    os.makedirs(os.path.expanduser(home))

    return (prefs, Cache(os.path.expanduser(home)))


class LaCommand(cmd.Cmd):
    prompt = 'lacli> '
    archive = None
    capsule = None
    certificate = None
    login = None

    def __init__(self, cache, prefs):
        cmd.Cmd.__init__(self)
        setupLogging(prefs['command']['debug'])
        registry = LaRegistry(cache, prefs, self)
        self.archive = LaArchiveCommand(registry)
        self.capsule = LaCapsuleCommand(registry)
        self.certificate = LaCertsCommand(registry)
        self.login = LaLoginCommand(registry)

    def do_EOF(self, line):
        print
        return True

    def dispatch(self, subcmd, options):
        options.insert(0, subcmd)
        try:
            subcmd = getattr(self, subcmd)
            line = subcmd.makecmd(docopt(subcmd.__doc__, options))
            self.dispatch_one(subcmd, line)
        except AttributeError:
            print "Unrecognized command:", subcmd
            print(__doc__)
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

    def do_login(self, line):
        self.login.onecmd('login ' + line)


def main(args=sys.argv[1:]):
    """Main function called by `laput` command.
    """
    options = docopt(__doc__.format(home=default_home),
                     version='lacli {}'.format(__version__),
                     options_first=True)
    prefs, cache = settings(options)
    cli = LaCommand(cache, prefs)
    if options['<command>']:
        cli.dispatch(options['<command>'], options['<args>'])
    elif options['--interactive']:
        cli.cmdloop()

if __name__ == "__main__":
    main()
