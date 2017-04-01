from functools import reduce

import itertools
import math


def flow(*functions):
    return lambda a: reduce(lambda x, f: f(x), functions, a)


def maybe_list(val=None):
    if val is None:
        return []
    return [val]


def andf(*fs):
    return lambda arg: all(map(lambda f: f(arg), fs))
