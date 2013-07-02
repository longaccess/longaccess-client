#!/home/kouk/code/bototest/bin/python
"""Upload a file to S3

Usage: laput.py [-d <sec>] [-D <level>] [-u <user>]
            [<filename>...]
       laput.py -h, --help

Options:
    -u <user>, --user <user>     username to request token for [default: testuser]
    -d <sec>, --duration <sec>   duration of token in seconds [default: 3600]
    -D <level>, --debug <level>  debugging level, from 0 to 2 [default: 0]

"""
     

import sys
from docopt import docopt
from lacli.upload import *
from lacli.command import LaCommand
from lacli import __version__
from latvm.tvm import MyTvm
from boto import config as boto_config

if __name__ == "__main__":
    options=docopt(__doc__, version='laput {}'.format(__version__))
    if not boto_config.has_section('Boto'):
        boto_config.add_section('Boto')
    boto_config.set('Boto','num_retries', '0')
    if options['--debug'] != '0':
        mp.util.log_to_stderr(mp.util.SUBDEBUG)
        boto_config.set('Boto','debug',options['--debug'])
    def tokens():
        tvm = MyTvm()
        while True:
            yield tvm.get_upload_token(options['--user'],options['--duration'])
    cli=LaCommand(tokens)
    if len(options['<filename>'])>0:
        for fname in options['<filename>']:
            cli.onecmd('put {}'.format(fname))
    else:
        cli.cmdloop()
