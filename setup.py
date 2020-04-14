#!/usr/bin/env python
# -*- test-case-name: twistedchecker -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from setuptools import find_packages, setup

with open('README.rst') as f:
    longDescription = f.read()

setup(
    name='twistedchecker',
    description='A Twisted coding standard compliance checker.',
    version='0.7.4',
    author='Twisted Matrix Laboratories',
    author_email='twisted-python@twistedmatrix.com',
    url='https://github.com/twisted/twistedchecker',
    packages=find_packages(),
    include_package_data=True,  # use MANIFEST.in during install
    entry_points={
      "console_scripts": [
          "twistedchecker = twistedchecker.core.runner:main"
      ]
    },
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Quality Assurance"
    ],
    keywords=[
        "twisted", "checker", "compliance", "pep8"
    ],
    install_requires=[
        'pylint>=2.4.4',
        'twisted>=15.0.0',
    ],
    extras_require = {
        'dev':  [
            'pyflakes',
            'coverage'
            ],
    },
    long_description=longDescription
)
