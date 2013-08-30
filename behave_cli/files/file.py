from functools import wraps


def file_vars(f):
    """ decorator to substitute filename vars in args and text """
    @wraps(f)
    def w(ctx, *args, **kwargs):
        filenames = dict(((n, f.name) for n, f in ctx.files.iteritems()))
        if ctx.text is not None:
            ctx.text = ctx.text.format(**filenames)
        args = [a.format(**filenames) for a in args]
        kwargs = dict(((k, v.format(**filenames))
                       for k, v in kwargs.items()))
        return f(ctx, *args, **kwargs)
    return w
