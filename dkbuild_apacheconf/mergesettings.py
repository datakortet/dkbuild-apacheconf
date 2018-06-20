# -*- coding: utf-8 -*-
import sys
import copy
import re
from past import builtins

__all__ = ['merge']


def _get_type(v):
    """Return the merge type of v.
    """
    if isinstance(v, bool):
        return 'bool'
    if isinstance(v, builtins.basestring):
        return 'string'
    if isinstance(v, list) or hasattr(v, 'append'):
        return 'list'
    if isinstance(v, dict) or hasattr(v, 'items'):
        return 'dict'

    return 'unknown'


def _merge_string(a, b):
    """Merge strings ``a`` and ``b``.

       If a contains a substitution marker, e.g.:

           'content of {#} a'

       then b will be inserted at {#}.

       If b contains a hole, e.g.:

           'contents of {_} b'

       then a will be inserted at {_}.

       You cannot have both a substitution and a hole.
    """
    parent_re = re.compile(r'{#}')
    child_re = re.compile(r'{_}')
    if parent_re.search(b) and child_re.search(a):
        raise TypeError(
            "You cannot specify both a hole and a substitution %r, %r" % (
                a, b
            ))
    if parent_re.search(b):
        return parent_re.sub(a, b)
    if child_re.search(a):
        return child_re.sub(b, a)
    return b


def _merge_list(a, b):
    return a + b


def _merge_bool(a, b):
    return b


def _merge_dict(a, b):
    res = {}
    for k, v in a.items():
        if k in b:
            res[k] = _merge_ab(a[k], b[k])
        else:
            res[k] = a[k]
    for k, v in b.items():
        if k not in a:
            res[k] = b[k]
    return res


def _merge_unknown(a, b):
    return b


def _merge_ab(a, b):
    """Returns a new object that is ``a`` merged with ``b``.
    """
    if callable(a) or a is None:
        return b
    at, bt = ab = _get_type(a), _get_type(b)
    if at != bt:
        raise TypeError("Incompatible types %s and %s (%r and %r)" % (
            at, bt, a, b
        ))
    return globals()['_merge_' + at](a, b)


def merge(*args):
    """Returns a new object that is all the ``arg`` in ``args``
       merge, left to right.
    """
    if len(args) == 0:
        return None
    res = copy.deepcopy(args[0])
    if len(args) == 1:
        return res
    for arg in args[1:]:
        res = _merge_ab(res, arg)
    return res
