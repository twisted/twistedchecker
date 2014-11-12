#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from setuptools import find_packages, setup


setup(
    name='TwistedChecker',
    description='A Twisted coding standard compliance checker.',
    version='0.3.0',
    author='Twisted Matrix Laboratories',
    author_email='twisted-python@twistedmatrix.com',
    url='https://github.com/twisted/twistedchecker',
    packages=find_packages(),
    package_data={
        "twistedchecker": ["configuration/pylintrc"]
    },
    scripts=[
        'bin/twistedchecker'
    ],
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Quality Assurance"
    ],
    keywords=[
        "twisted", "checker", "compliance", "pep8"
    ],
    install_requires=[
        "pylint == 0.26.0",
        "logilab-common == 0.62.0",
        "pep8 == 1.5.7"
    ],
    long_description=file('README.rst').read()
)
