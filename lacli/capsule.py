import urllib
import re

from lacli.log import getLogger
from urlparse import urlparse


def archive_capsule(docs):
    links = docs.get('links')
    if links is None or not links.upload:
        return None
    try:
        return urllib.unquote(
            re.search(
                r'C:([^:]*):',
                urlparse(links.upload).fragment
            ).group(1)
        ).decode('utf8')
    except Exception:
        getLogger().debug("no capsule information found", exc_info=True)


def archive_uri(uri, capsule=None):
    if capsule is not None:
        assert '#' not in uri
        uri += '#C:{}:'.format(
            urllib.quote(capsule.encode('utf8')))
    return uri
