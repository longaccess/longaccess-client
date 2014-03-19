from lacli.date import parse_timestamp, epoch


def creation(docs):
    """ return signature creation, or if not available, the archive creation.
        For sorting purposes. Invalid timestamps sort to the start of the epoch
    """
    created = docs['archive'].meta.created
    sig = docs.get('signature')
    if sig and sig.created:
        created = sig.created
    tstamp = parse_timestamp(created)
    if not tstamp:
        tstamp = epoch()
    return tstamp


def archive_size(archive):
    size = ""
    if archive.meta.size:
        kib = archive.meta.size // 1024
        mib = kib // 1024
        gib = mib // 1024

        if not kib:
            size = "{} B".format(archive.meta.size)
        elif not mib:
            size = "{} KB".format(kib)
        elif not gib:
            size = "{} MB".format(mib)
        else:
            size = "{} GB".format(gib)
    return size
