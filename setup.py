#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""dkbuild-apacheconf - short description
"""

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Topic :: Software Development :: Libraries
"""

import sys
import setuptools
from distutils.core import setup, Command
from setuptools.command.test import test as TestCommand

version = '0.1.0'


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='dkbuild-apacheconf',
    version=version,
    requires=[],
    install_requires=[],
    description=__doc__.strip(),
    classifiers=[line for line in classifiers.split('\n') if line],
    long_description=open('README.rst').read(),
    cmdclass={'test': PyTest},
    packages=['dkbuild_apacheconf'],
    entry_points={
        'console_scripts': """
            dkbuild-apacheconf = dkbuild_apacheconf.__main__:main
        """
    },
    zip_safe=False,
)
