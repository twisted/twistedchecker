#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Distutils installer for TwistedChecker.
"""

import sys, os

try:
    from setuptools import setup
except ImportError:
    pass



def main(args):
    """
    Install TwistedChecker.
    """
    setup(
        name='TwistedChecker',
        version='0.1.0',
        author='Twisted Matrix Laboratories',
        author_email='twisted-python@twistedmatrix.com',
        packages=[
            'twistedchecker',
            'twistedchecker.configuration',
            'twistedchecker.functionaltests',
            'twistedchecker.test',
            'twistedchecker.checkers',
            'twistedchecker.core',
            'twistedchecker.reporters'
            ],
        data_files=[
            ('twistedchecker/configuration', ['twistedchecker/configuration/pylintrc'])
            ],
        scripts=['bin/twistedchecker'],
        url='http://pypi.python.org/pypi/TwistedChecker/',
        license='MIT',
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Topic :: Software Development :: Quality Assurance"
            ],
        install_requires=[
            "pylint==0.26.0",
            "pep8==1.3.3"
            ],
        description='A code standards checker for Twisted.',
        long_description="""\
TwistedChecker is a code standards checker, originally designed for the use of
the Twisted project. It tests Python code for problems such as PEP8 compliance,
docstrings, trailing spaces and strange variable naming.
""",
        )


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(1)