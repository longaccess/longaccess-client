from lacore.adf.persist import make_adf
from lacli.hash import HashIO


def archive_handle(docs):
    h = HashIO()
    make_adf(docs, out=h)
    return h.getvalue().encode('hex')
