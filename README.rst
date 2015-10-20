Twisted Coding Standard Checker
===============================

TwistedChecker checks Python code for compliance with the `Twisted coding
standard <https://twistedmatrix.com/documents/current/core/development/policy/coding-standard.html>`.

This was originally a project of Google Summer of Code 2012.

TwistedChecker's dependencies are recorded in setup.py.


Development
-----------

.. image:: https://travis-ci.org/twisted/twistedchecker.svg?branch=master
    :target: https://travis-ci.org/twisted/twistedchecker

.. image:: https://badge.fury.io/py/TwistedChecker.svg
    :target: https://badge.fury.io/py/TwistedChecker

Get a development environment::

    virtualenv build
    . build/bin/activate
    pip install -Ue '.[dev]'

To test twistedchecker, run the following in the source directory::

    trial twistedchecker

Check pyflakes status ignoring functional tests
(#68 some day we might use twistedchecker on itself)::

    python check_pyflakes.py twistedchecker/
