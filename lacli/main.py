#!/home/kouk/code/bototest/bin/python
"""Upload a file to Long Access

Usage: laput.py [-d <sec>] [-D <level>] [-u <user>] [-p <pass>]
            [-b <bucket> ] [-np <np>] [<filename>...]
       laput.py -h, --help

Options:
    -u <user>, --user <user>       user name
    -p <pass>, --password <pass>   user password
    -d <sec>, --duration <sec>     duration of token in seconds [default: 3600]
    -D <level>, --debug <level>    debugging level, from 0 to 2 [default: 0]
    -b <bucket>, --bucket <bucket> bucket to upload to [default: lastage]
    -np <np>, --procs <np>         number of processes [default: auto]

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
        pwd=options['--pass'],
        secs=options['--duration'],
        bucket=options['--bucket'],
        debug=int(options['--debug']),
        nprocs=options['--procs'])
    cli = LaCommand(session, debug=int(options['--debug']))
    if len(options['<filename>']) > 0:
        for fname in options['<filename>']:
            cli.onecmd('put {}'.format(fname))
    else:
        cli.cmdloop()

if __name__ == "__main__":
    main()
