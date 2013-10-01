#!/home/kouk/code/bototest/bin/python
"""Upload a file to Long Access

Usage: lacli put [-d <sec>] [-D <level>] [-u <user>] [-p <pass>]
            [-b <bucket> ] [-n <np>] <filename>...
       lacli list [-u <user>] [-p <pass>]
       lacli [-u <user>] [-p <pass>]
       lacli -h, --help

Options:
    -u <user>, --user <user>       user name
    -p <pass>, --password <pass>   user password
    -d <sec>, --duration <sec>     duration of token in seconds [default: 3600]
    -D <level>, --debug <level>    debugging level, from 0 to 2 [default: 0]
    -b <bucket>, --bucket <bucket> bucket to upload to [default: lastage]
    -n <np>, --procs <np>         number of processes [default: auto]

"""


import sys
from docopt import docopt
from lacli.command import LaCommand
from lacli import __version__
from lacli.log import setupLogging
from lacli.session import Session


def main(args=sys.argv[1:]):
    """Main function called by `laput` command.
    """
    options = docopt(__doc__, version='laput {}'.format(__version__))
    setupLogging(int(options['--debug']))
    session = Session(
        uid=options['--user'],
        pwd=options['--password'],
        secs=options['--duration'],
        bucket=options['--bucket'],
        debug=int(options['--debug']),
        nprocs=options['--procs'])
    cli = LaCommand(session, debug=int(options['--debug']))
    if options['put']:
        for fname in options['<filename>']:
            cli.onecmd('put {}'.format(fname))
    elif options['list']:
        cli.onecmd('list')
    else:
        cli.cmdloop()

if __name__ == "__main__":
    main()
