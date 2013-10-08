def filename_vars(ctx):
    return dict(((n, f.name) for n, f in ctx.files.iteritems()))


def dirname_vars(ctx):
    return dict(((n, d) for n, d in ctx.dirs.iteritems()))
