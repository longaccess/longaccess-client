"""encrypt a file using simple AES-CTR-256

Usage: laenc <file>
"""

import sys
from docopt import docopt
from tempfile import NamedTemporaryFile
from lacli.crypt import CryptIO
from lacli.cipher import new_key
from lacli.cipher.aes import CipherAES
from shutil import copyfileobj


def main(args=sys.argv[1:]):
    options = docopt(__doc__)
    with open(options['<file>']) as f:
        with NamedTemporaryFile(delete=False, mode='w') as out:
            key = new_key(256)
            with CryptIO(out, CipherAES(key), mode='w') as cf:
                copyfileobj(f, cf)
                print "saved in", out.name, "key is", key.encode('hex')

if __name__ == "__main__":
    main()
