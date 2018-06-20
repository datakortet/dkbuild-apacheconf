# -*- coding: utf-8 -*-
from dkbuild_apacheconf.mergesettings import merge
import pytest


def test_hole():
    assert merge('hello {_}', 'world') == 'hello world'
    assert merge('world', 'hello {#}') == 'hello world'

    with pytest.raises(TypeError):
        merge('{_}', '{#}')


def test_merge_dict():
    a = dict(a=42)
    b = dict(b=[])
    assert merge(a, b) == dict(a=42, b=[])


def test_merge_dict2():
    a = dict(a=42, b=[42])
    b = dict(b=[])
    assert merge(a, b) == dict(a=42, b=[42])


def test_merge_dict3():
    a = dict(b=dict(c=[42]))
    b = dict(b=dict())
    assert merge(a, b) == dict(b={'c': [42]})


def test_merge_string():
    assert merge('hello', 'world') == 'world'


def test_merge_bool():
    assert merge(True, False) == False


def test_merge_unknown():
    assert merge(object(), 42) == 42
    assert merge(None, 42) == 42
    assert merge(lambda:42, 42) == 42


def test_merge_difftype():
    with pytest.raises(TypeError):
        merge(42, 'hello')


def test_edge_cases():
    assert merge() == None
    assert merge(42) == 42
