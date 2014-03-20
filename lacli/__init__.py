from __future__ import unicode_literals
import platform

try:
    from lacli.version import __version__
except ImportError:
    __version__ = "0.2.6a1"


def get_client_info(terse=False):
    el = ["Longaccess client"]
    el.append(__version__)
    el.append(platform.platform(True, terse))
    el.append("py"+platform.python_version())
    el.append(platform.machine())
    return " ".join(el)
# vim: et:sw=4:ts=4
