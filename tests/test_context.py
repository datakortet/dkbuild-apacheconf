# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import pytest
import json
from dkbuild_apacheconf.context import find_server_ini, read_ini, Context
from dkbuild_apacheconf.errors import NoServerIniError

CURDIR = os.path.normcase(os.path.abspath(os.path.dirname(__file__)))

class pset(dict):
    def __init__(self, **kw):
        self.__dict__ = self
        self.__dict__.update(kw)


def test_find_server_ini():
    args = pset(site='site-test.ini', server='server-test.ini')
    # print(dict(args.__dict__))
    assert find_server_ini([], args) == os.path.join(CURDIR, 'server-test.ini')

    with pytest.raises(NoServerIniError):
        find_server_ini([], pset(site='site-test.ini', server='foo'))


def test_read_ini():
    vals = read_ini(['site-test.ini', 'server-test.ini'])
    print(json.dumps(dict(vals), indent=4))
    assert vals['debug']['port'] == 8001


def test_context():
    ctx = Context(
        [], pset(
            site='site-test.ini',
            server='server-test.ini',
            skip_server=False,
            verbose=True,
        )
    )

    print(ctx)
    assert ctx['ssl']['key_file'] == 'asdf.key'
