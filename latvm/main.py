#!/home/kouk/code/bototest/bin/python
"""Initialize the TVM

Usage: lacreds.py init -k <key> -s <secret>
       lacreds.py remove
       lacreds.py list
       lacreds.py -h, --help

Options:
    -k <key>, --key <key>           the AWS key
    -s <secret>, --secret <secret>  the AWS secret

"""
import os
import errno
import sys
from docopt import docopt
from latvm.tvm import MyTvm
from latvm import __version__


def main(args=sys.argv[1:]):
    """Main function called by `lacreds` command.
    """
    options = docopt(__doc__, version='lacreds {}'.format(__version__))
    if options['init']:
        MyTvm.storecreds(options['--key'], options['--secret'])
    elif options['list']:
        if os.path.isfile(MyTvm.credfile):
            with open(MyTvm.credfile) as f:
                import json
                print "AWS Accesskey: {}".format(json.loads(f.read())['key'])
    elif options['remove']:
        try:
            os.remove(MyTvm.credfile)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

if __name__ == "__main__":
    main()
