from __future__ import unicode_literals
from lacore import get_client_info as lacore_info

try:
    from lacli.version import __version__
except ImportError:
    __version__ = "0.2.6"


def get_client_info(terse=False):
    el = ["Longaccess client"]
    el.append(__version__)
    el.append(lacore_info(terse))
    return " ".join(el)
# vim: et:sw=4:ts=4
