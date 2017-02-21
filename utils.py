from functools import reduce


def flow(*functions):
    return lambda a: reduce(lambda x, f: f(x), functions, a)


def unlines(arr, elem_str=str):
    return str.join('\n', map(elem_str, arr))
