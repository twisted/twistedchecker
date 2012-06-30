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
     'W9601': ('Use print() instead of print statement in Python 3',
               'Checking print statement for python 3.'),
    }
    options = ()
    linesOfCurrentModule = None

    def visit_module(self, node):
        """
        Save lines of the module currently checking.
        """
        self.linesOfCurrentModule = node.file_stream.readlines()


    def visit_print(self, node):
        """
        Be invoked when visiting a print statement.
        """
        linenoBegin = node.fromlineno - 1
        linenoEnd = node.tolineno - 1
        if (not self.linesOfCurrentModule or
            linenoEnd >= len(self.linesOfCurrentModule)):
            # in the case, the code is not from a module exists
            return
        codeStatement = " ".join(
                [line.strip()
                 for line in \
                 self.linesOfCurrentModule[linenoBegin: linenoEnd + 1]])
        # check for parens
        # replace all child nodes(especially tuples) with X
        codeStatement = codeStatement.replace(" ", "")
        for childNode in node.get_children():
            # do not replace for empty tuple
            if childNode.as_string() == "()":
                continue
            codeChildNode = childNode.as_string().replace(" ", "")
            codeStatement = codeStatement.replace(codeChildNode, "X")
        if not re.search("print\(.*?\)", codeStatement):
            self.add_message('W9601', node=node)
