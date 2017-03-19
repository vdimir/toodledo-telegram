from functools import reduce

import math


def flow(*functions):
    return lambda a: reduce(lambda x, f: f(x), functions, a)


def unlines(arr, elem_str=str):
    return str.join('\n', map(elem_str, arr))


def group_sq(l):
    sqlen = lambda lst: math.ceil(math.sqrt(len(lst)))
    if not isinstance(l, list):
        l = list(l)
    return [l[i:i + sqlen(l)] for i in range(0, len(l), sqlen(l))]
