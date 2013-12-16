# thanks to mathieu larose: http://mathieularose.com/function-composition-in-python


import functools

def compose(*functions):
    def compose2(f, g):
        return lambda x: f(g(x))
    return functools.reduce(compose2, functions)
