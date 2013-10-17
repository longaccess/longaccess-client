"""Upload a file to Long Access

Usage: lacli [--help] [-u <user>] [-p <pass>] [--verbose]
             [--home <home>] [--debug <level>] [--batch]
             [<command> [<args>...]]

Commands (run lacli <command> -h for options):

    archive         manage archives
    capsule         manage capsules
    certificate     manage certificates

Options:
    -u <user>, --user <user>       user name
    -p <pass>, --password <pass>   user password
    -d <level>, --debug <level>    debug level, from 0 to 2 [default: 0]
    --home <home>                  conf/cache dir [default: ~/.longaccess]
    -v, --verbose                  print verbose information
    --batch                        be brief, don't ask questions
    -h, --help                     print this help
"""


import sys
import os
from docopt import docopt
from lacli.command import LaCommand
from lacli import __version__
from lacli.api import Api
from lacli.cache import Cache


def settings(options):
    debug = 0

    try:
        debug = int(options['--debug'])
    except ValueError:
        print "error: illegal value for 'debug' parameter."
        raise

    verify = True
    if '0' == os.getenv('LA_API_VERIFY'):
        verify = False

    batch = options['--batch']
    if not batch and os.getenv('LA_BATCH_OPERATION'):
        batch = True

    prefs = {
        'api': {
            'user': options['--user'],
            'pass': options['--password'],
            'url': os.getenv('LA_API_URL'),
            'verify': verify
        },
        'command': {
            'debug': debug,
            'verbose': options['--verbose'],
            'batch': options['--batch']
        },
    }
    if options['<command>']:
        prefs[options['<command>']] = options['<args>']
    return (prefs, Cache(os.path.expanduser(options['--home'])))


def main(args=sys.argv[1:]):
    """Main function called by `laput` command.
    """
    options = docopt(__doc__,
                     version='lacli {}'.format(__version__),
                     options_first=True)
    prefs, cache = settings(options)
    api = Api(prefs['api'])
    cli = LaCommand(api, cache, prefs)
    if options['<command>']:
        cli.dispatch(options['<command>'], options['<args>'])
    else:
        cli.cmdloop()

if __name__ == "__main__":
    main()
