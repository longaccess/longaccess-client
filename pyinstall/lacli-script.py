import lacli.main
import os
import sys
import multiprocessing
os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(
    os.path.dirname(sys.executable), 'cacert.pem')
multiprocessing.freeze_support()
lacli.main.main()
