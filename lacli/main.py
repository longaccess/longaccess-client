#!/home/kouk/code/bototest/bin/python
"""Upload a file to Long Access

Usage: lacli put [options] [-b <bucket> ] [-n <np>] <filename>...
       lacli list [options]
       lacli archive [options]
       lacli [options]
       lacli -h, --help

Options:
    -u <user>, --user <user>       user name
    -p <pass>, --password <pass>   user password
    -d <level>, --debug <level>    debugging level, from 0 to 2 [default: 0]
    -b <bucket>, --bucket <bucket> bucket to upload to [default: lastage]
    -n <np>, --procs <np>          number of processes [default: auto]
    --home <home>                  conf/cache dir [default: ~/.longaccess]

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

    return (
        {
            'api': {
                'user': options['--user'],
                'pass': options['--password'],
                'url': os.getenv('LA_API_URL'),
            },
            'upload': {
                'bucket': options['--bucket'],
                'nprocs': nprocs,
                'retries': 4,
                'debugworker': debug > 2
            },
            'command': {
                'debug': debug
            },
        },
        Cache(options['--home']))


def main(args=sys.argv[1:]):
    """Main function called by `laput` command.
    """
    options = docopt(__doc__, version='laput {}'.format(__version__))
    prefs, cache = settings(options)
    cli = LaCommand(Api(prefs['api']), cache, prefs)
    if options['put']:
        for fname in options['<filename>']:
            cli.onecmd('put {}'.format(fname))
    elif options['list']:
        cli.onecmd('list')
    elif options['archive']:
        cli.onecmd('archive')
    else:
        cli.cmdloop()

if __name__ == "__main__":
    main()
