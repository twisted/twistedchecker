#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Distutils installer for TwistedChecker.
"""

try:
    from setuptools import setup
except ImportError:
    pass

import sys, os


def main(args):
    """
    Install TwistedChecker.
    """
    setup(
        name='TwistedChecker',
        version='0.1.0',
        author='Raphael Shu',
        author_email='raphael@uaca.com',
        packages=['twistedchecker', 'twistedchecker.configuration', 
                  'twistedchecker.functionaltests', 'twistedchecker.test',
                  'twistedchecker.checkers', 'twistedchecker.core',
                  'twistedchecker.reporters'],
        data_files=[('twistedchecker/configuration', ['twistedchecker/configuration/pylintrc'])],
        scripts=['bin/twistedchecker'],
        url='http://pypi.python.org/pypi/TwistedChecker/',
        license='LICENSE',
        description='A code checker for Twisted.',
        long_description=open('README').read(),
        install_requires=[
            "pylint >= 0.25.1",
            "pep8 >= 1.3.3",
            "logilab-astng >= 0.23.1"
        ],
    )
    

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(1)

