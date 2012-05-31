import sys

from logilab import astng
from logilab.common.ureports import Table
from logilab.astng import are_exclusive

from pylint.interfaces import IASTNGChecker
from pylint.reporters import diff_string
from pylint.checkers import BaseChecker, EmptyReport
from pylint.checkers.utils import check_messages, clobber_in_except, is_inside_except

class CopyrightChecker(BaseChecker):
    """
    A checker for checking copyright headers.
    Every Twisted file should have copyright header like bellow:
    # Copyright (c) Twisted Matrix Laboratories.
    # See LICENSE for details.
    """
    msgs = {
     'W9001': ('# Missing copyright header',
               '# Used when a python file of Twisted has no copyright header.'),
    }
    __implements__ = IASTNGChecker
    name = 'copyright'
    options = ()
    commentsRequired = ("Copyright (c) Twisted Matrix Laboratories.",
                          "See LICENSE for details.")

    def visit_module(self, node):
        """
        A interface will be called when visiting a module.
        """
        self._checkCopyright('module', node)


    def _checkCopyright(self, node_type, node):
        """
        Check the module has no copyright header
        """
        text = open(node.file).read()
        for docstring in self.commentsRequired:
            if text.count(docstring) == 0:
                self.add_message('W9001', node=node)
                break
