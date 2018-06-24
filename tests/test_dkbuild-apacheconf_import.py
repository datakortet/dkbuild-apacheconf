# -*- coding: utf-8 -*-

"""Test that all modules are importable.
"""

import dkbuild_apacheconf
import dkbuild_apacheconf.__main__
import dkbuild_apacheconf.context
import dkbuild_apacheconf.defaults
import dkbuild_apacheconf.errors
import dkbuild_apacheconf.mergesettings


def test_import_():
    "Test that all modules are importable."
    
    assert dkbuild_apacheconf
    assert dkbuild_apacheconf.__main__
    assert dkbuild_apacheconf.context
    assert dkbuild_apacheconf.defaults
    assert dkbuild_apacheconf.errors
    assert dkbuild_apacheconf.mergesettings
