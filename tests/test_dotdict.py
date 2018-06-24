# -*- coding: utf-8 -*-
import textwrap

import pytest

from dkbuild_apacheconf.dotdict import dotdict


def test_add_depth1():
    dd = dotdict()
    dd['hello'] = 42
    print(dd)
    assert dd.ctx == { 'hello': 42 }


def test_add_depth2():
    dd = dotdict()
    dd['hello.world'] = 42
    print(dd)
    assert dd.ctx == {
        'hello': {
            'world': 42
        }
    }


def test_add_err():
    dd = dotdict()
    with pytest.raises(TypeError):
        dd[42] = 'hello world'


def test_get():
    dd = dotdict()
    dd['hello.world'] = 42
    assert dd['hello.world'] == 42
    assert dd.get('hello.world') == 42


def test_get_default():
    dd = dotdict()
    assert dd.get('hello.world', 42) == 42
    assert dd.get('hello.world') is None


def test_serialization():
    dd = dotdict()
    dd['hello.world'] = 42
    assert str(dd) == textwrap.dedent("""\
    <dotdict {
        "hello": {
            "world": 42
        }
    }>""")
    assert repr(dd) == textwrap.dedent("""\
    <dotdict {
        "hello.world": 42
    }>""")
