import math


def simple(a):
    return a


def with_op(a):
    return a + 5


def with_call(a):
    return math.pow(a, 2)


def _b(a):
    return a


def with_direct_call(a):
    return _b(a)
