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
        res = getattr(obj, name, default)
        if res is None:
            return default
        return res
    return wrap


def tuple_func(*fs):
    def wrap(arg):
        return tuple(map(lambda f: f(arg), fs))
    return wrap


def andf(*fs):
    return lambda arg: all(map(lambda f: f(arg), fs))

class Maybe:
    def __init__(self, val):
        self.val = val

    @staticmethod
    def _to_maybe(val):
        if isinstance(val, Maybe):
            return val
        else:
            return Maybe(val)

    def or_else(self, val):
        if self.val is None:
            return Maybe._to_maybe(val)
        return self


class Inf:
    def __init__(self, great=True):
        self.great = great

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.great == self.great
        return False

    def __lt__(self, other):
        return not self.great

    def __gt__(self, other):
        return self.great

    def __le__(self, other):
        if self == other:
            return True
        return not self.great

    def __ge__(self, other):
        if self == other:
            return True
        return self.great
