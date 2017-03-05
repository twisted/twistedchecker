"""
TwistedChecker

A project of GSoC 2012 to checker for codes of twisted.
"""

import os
import sys

# set the absolute path of TwistedChecker
abspath = os.path.dirname(os.path.abspath(__file__))

version = getattr(sys, "version_info", (0,))
if version < (2, 7):
    raise ImportError("TwistedChecker requires Python 2.7 or Python 3.5+ ")
elif version >= (3, 0) and version < (3, 5):
    raise ImportError("TwistedChecker on Python 3 requires Python 3.5+")
