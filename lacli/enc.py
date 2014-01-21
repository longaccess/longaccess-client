import sys


fsenc = sys.getfilesystemencoding() or "UTF-8"


def get_unicode(value):
    if isinstance(value, unicode):
        return value
    try:
        return unicode(value, 'UTF-8')
    except UnicodeDecodeError:
        if fsenc == 'UTF-8':
            raise
        return unicode(value, fsenc)
# vim: et:sw=4:ts=4
