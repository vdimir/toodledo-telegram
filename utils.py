from functools import reduce

import itertools
import math


def flow(*functions):
    return lambda a: reduce(lambda x, f: f(x), functions, a)


def maybe_list(val=None):
    if val is None:
        return []
    return [val]


def attrgetter(name, default=None):
    def wrap(obj):
        return getattr(obj, name, default) or default
    return wrap


def andf(*fs):
    return lambda arg: all(map(lambda f: f(arg), fs))


class Inf:
    def __init__(self, great=True):
        self.great = great

    def __lt__(self, other):
        neq = not isinstance(other, self.__class__)
        return neq and not self.great

    def __gt__(self, other):
        neq = not isinstance(other, self.__class__)
        return neq and self.great
