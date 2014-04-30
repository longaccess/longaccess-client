from lacore.adf.persist import make_adf
from lacore.archive import restore_archive as _restore_archive
from lacli.nice import with_low_priority
from lacli.hash import HashIO


def archive_handle(docs):
    h = HashIO()
    make_adf(docs, out=h)
    return h.getvalue().encode('hex')

restore_archive = with_low_priority(_restore_archive)
