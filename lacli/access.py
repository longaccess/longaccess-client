
import os,errno
from docopt import docopt
from latvm.tvm import MyTvm
from latvm import __version__

def put_cmd():
    options=docopt(__doc__, version='lacreds {}'.format(__version__))
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

