#!/usr/bin/env python

import os
import sys

sys.path.insert(0, os.path.abspath(os.getcwd()))

from twistedchecker.core.runner import Runner

Runner().run(sys.argv[1:])
