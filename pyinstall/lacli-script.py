import lacli.main
import os
import sys
os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(
    os.path.dirname(sys.executable), 'cacert.pem')
lacli.main.main()
