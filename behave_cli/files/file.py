def filename_vars(ctx):
    return dict(((n, f.name) for n, f in ctx.files.iteritems()))
