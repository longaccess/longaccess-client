#!/home/kouk/code/bototest/bin/python

import sys
import argparse 
from lacli.upload import *
from lacli.command import LaCommand
from boto import config as boto_config

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='parallel upload to S3')
    argparser.add_argument('-u','--federated-user', dest='user', 
        default='testuser', help='user id of uploading user' )
    argparser.add_argument('-d','--duration',  dest='duration', 
        default=3600, help='duration of federated token in seconds')
    argparser.add_argument('-D', '--debug', dest='debug', 
        default='0', help='Enable Boto debugging (0,1 or 2)')
    argparser.add_argument('filename', nargs='*', help='filenames to upload')
    options = argparser.parse_args()
    if not boto_config.has_section('Boto'):
        boto_config.add_section('Boto')
    boto_config.set('Boto','num_retries', '0')
    if options.debug != '0':
        mp.util.log_to_stderr(mp.util.SUBDEBUG)
        boto_config.set('Boto','debug',options.debug)
    cli=LaCommand(options)
    if len(options.filename)>0:
        for fname in options.filename:
            cli.onecmd('put {}'.format(fname))
    else:
        cli.cmdloop()
