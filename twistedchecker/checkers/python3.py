"""
Checker for python3 compatibility issues.
"""
import sys
import os
import re
from logilab import astng

import logilab.astng.node_classes

from pylint.interfaces import IASTNGChecker
from pylint.checkers import BaseChecker
from pylint.checkers import utils


class Python3Checker(BaseChecker):
    """
    Checker for python3 compatibility issues.
    """

    __implements__ = (IASTNGChecker,)
    name = 'python3'
    msgs = {
     'W9601': ('For compatibility with python 3,'
               'you should import print_function from __future__',
               'Checking print statement for python 3.'),
    }
    options = ()
    warningsOfCurrentModule = None

    def visit_module(self, node):
        """
        Save lines of the module currently checking.

        @param node: current node of checking
        """
        self.warningsOfCurrentModule = set([])


    def visit_print(self, node):
        """
        Be invoked when visiting a print statement.

        @param node: current node of checking
        """
        if self.warningsOfCurrentModule == None:
            return
        if "W9601" not in self.warningsOfCurrentModule:
            self.warningsOfCurrentModule.add("W9601")
            self.add_message('W9601', node=node.root())
