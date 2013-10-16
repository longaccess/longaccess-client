"""Upload a file to Long Access

Usage: lacli put [options] [-c <capsule> ] [-n <np>] [<archive>]
       lacli list [options]
       lacli archive [options] [-t <title>] [<dirname>]
       lacli restore [options] [-o <dirname>] [<archive>]
       lacli status [options] [<upload-index>]
       lacli [options]
       lacli -h, --help

Command description:

    put:      upload a prepared archive to a capsule in Long Access. If no
              archive index is specified the first listed (see the "archive"
              command)

    list:     list capsules available in Long Access.

    archive:  manage prepared archives. Create a new archive if the directory
              name argument is present. With no argument it lists prepared
              archives.

    restore:  restore a downloaded archive. If no archive index is specified
              the first listed (see "archive") is restored.

    status:   display pending archive uploads. If an upload index is specified
              it polls the API for the status and updates the application
              cache.

Options:
    -u <user>, --user <user>            user name
    -p <pass>, --password <pass>        user password
    -d <level>, --debug <level>         debug level, from 0 to 2 [default: 0]
    -b <bucket>, --bucket <bucket>      bucket to upload to [default: lastage]
    -n <np>, --procs <np>               number of processes [default: auto]
    --home <home>                       conf/cache dir [default: ~/.longaccess]
    -t <title>, --title <title>         title for prepared archive
    -o <dirname>, --out <dirname>       directory to restore archive
    -c <capsule>, --capsule <capsule>   capsule to upload to [default: 1]
    -v, --verbose                       print verbose information
    --batch                             be brief, don't ask questions

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

    verify = True
    if '0' == os.getenv('LA_API_VERIFY'):
        verify = False

    batch = options['--batch']
    if not batch and os.getenv('LA_BATCH_OPERATION'):
        batch = True

    return (
        {
            'api': {
                'user': options['--user'],
                'pass': options['--password'],
                'url': os.getenv('LA_API_URL'),
                'verify': verify
            },
            'upload': {
                'bucket': options['--bucket'],
                'nprocs': nprocs,
                'retries': 4,
                'debugworker': debug > 2
            },
            'command': {
                'debug': debug,
                'verbose': options['--verbose'],
                'batch': options['--batch']
            },
        },
        Cache(os.path.expanduser(options['--home'])))


def main(args=sys.argv[1:]):
    """Main function called by `laput` command.
    """
    options = docopt(__doc__, version='laput {}'.format(__version__))
    prefs, cache = settings(options)
    cli = LaCommand(Api(prefs['api']), cache, prefs)
    if options['put']:
        capsule = 1
        try:
            capsule = int(options['--capsule'])
        except ValueError:
            print "error: illegal value for 'capsule' parameter."
            raise

        with cli.temp_var(capsule=capsule):
            a = options['<archive>']
            if a:
                cli.onecmd('put {}'.format(a))
            else:
                cli.onecmd('put')
    elif options['list']:
        cli.onecmd('list')
    elif options['archive']:
        d = options['<dirname>']
        if d:
            with cli.temp_var(archive_title=options['--title']):
                cli.onecmd('archive {}'.format(d))
        else:
            cli.onecmd('archive')
    elif options['restore']:
        cmd = 'restore '
        if options['<archive>']:
            cmd += options['<archive>']
        with cli.temp_var(output_directory=options['--out']):
            cli.onecmd(cmd)
    elif options['status']:
        cmd = 'status  '
        if options['<upload-index>']:
            cmd += options['<upload-index>']
        cli.onecmd(cmd)
    else:
        cli.cmdloop()

if __name__ == "__main__":
    main()
