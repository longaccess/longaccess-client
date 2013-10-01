from functools import wraps


def format_vars(f):
    """ decorator to substitute vars in args and text """
    @wraps(f)
    def w(ctx, *args, **kwargs):
        vs = {}
        for cb in ctx.format_vars:
            vs.update(cb(ctx))  # merge all var dicts
        if ctx.text is not None:
            ctx.text = ctx.text.format(**vs)
        args = [a.format(**vs) for a in args]
        kwargs = dict(((k, v.format(**vs))
                       for k, v in kwargs.items()))
        return f(ctx, *args, **kwargs)
    return w
