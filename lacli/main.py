#!/home/kouk/code/bototest/bin/python
"""Upload a file to Long Access

Usage: lacli put [-d <level>] [-u <user>] [-p <pass>]
            [-b <bucket> ] [-n <np>] <filename>...
       lacli list [-u <user>] [-p <pass>]
       lacli [-u <user>] [-p <pass>]
       lacli -h, --help

Options:
    -u <user>, --user <user>       user name
    -p <pass>, --password <pass>   user password
    -d <level>, --debug <level>    debugging level, from 0 to 2 [default: 0]
    -b <bucket>, --bucket <bucket> bucket to upload to [default: lastage]
    -n <np>, --procs <np>         number of processes [default: auto]

"""


import sys
import os
from docopt import docopt
from lacli.command import LaCommand
from lacli import __version__
from lacli.api import Api


def settings(options):
    debug = 0
    nprocs = None

    try:
        debug = int(options['--debug'])
    except ValueError:
        print "error: illegal value for 'debug' parameter."
        raise

    try:
        if options['--procs'] != 'auto':
            nprocs = int(options['--procs'])
    except ValueError:
        print "error: illegal value for 'procs' parameter."
        raise

    return {
        'api': {
            'user': options['--user'],
            'pass': options['--password'],
            'url': os.getenv('LA_API_URL'),
        },
        'upload': {
            'bucket': options['--bucket'],
            'nprocs': nprocs,
        },
        'command': {
            'debug': debug
        },
    }


def main(args=sys.argv[1:]):
    """Main function called by `laput` command.
    """
    options = docopt(__doc__, version='laput {}'.format(__version__))
    prefs = settings(options)
    cli = LaCommand(Api(prefs['api']), prefs)
    if options['put']:
        for fname in options['<filename>']:
            cli.onecmd('put {}'.format(fname))
    elif options['list']:
        cli.onecmd('list')
    else:
        cli.cmdloop()

if __name__ == "__main__":
    main()
