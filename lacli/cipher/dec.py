"""decrypt a file using simple AES-CTR-256

Usage: ladec <file> <key>
"""

import sys
from docopt import docopt
from .aes import CipherAES
from ..crypt import CryptIO
from tempfile import NamedTemporaryFile
from shutil import copyfileobj


def main(args=sys.argv[1:]):
    options = docopt(__doc__)
    with open(options['<file>']) as f:
        with CryptIO(f, CipherAES(options['<key>'].decode('hex'))) as cf:
            with NamedTemporaryFile(delete=False) as out:
                copyfileobj(cf, out)
                print "saved in", out.name

if __name__ == "__main__":
    main()
