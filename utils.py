from functools import reduce


def flow(*functions):
    return lambda a: reduce(lambda x, f: f(x), functions, a)


