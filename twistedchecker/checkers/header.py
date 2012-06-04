import sys
import re

from logilab import astng
from logilab.common.ureports import Table
from logilab.astng import are_exclusive

from pylint.interfaces import IASTNGChecker
from pylint.reporters import diff_string
from pylint.checkers import BaseChecker, EmptyReport

class HeaderChecker(BaseChecker):
    """
    A checker for checking headers.
    Moudles must have a copyright message, a docstring and
    a reference to a test module that contains the bulk of its tests.
    Copyright should like this:
    # Copyright (c) Twisted Matrix Laboratories.
    # See LICENSE for details.
    Reference of test module should like this:
    # -*- test-case-name: <test module> -*-
    """
    msgs = {
     'W9001': ('Missing copyright header',
               'Used when a module of Twisted has no copyright header.'),
     'W9002': ('Missing a reference to test module in header',
               'Used when a module does not contain a reference'
               ' to test module.'),
     'W9003': ('Missing docstring of this module',
               'Used when a module does not contain docstring'),
    }
    __implements__ = IASTNGChecker
    name = 'header'
    options = ()
    commentsCopyright = ("# Copyright (c) Twisted Matrix Laboratories.",
                        "# See LICENSE for details.")
    patternTestReference = \
     r"# -\*- test-case-name: (([a-z_][a-z0-9_]*)\.)*[a-z_][a-z0-9_]* -\*-"


    def visit_module(self, node):
        """
        A interface will be called when visiting a module.

        @param node: node of current module
        """
        if not node.file_stream:
            # failed to open the module
            return
        text = node.file_stream.read()
        self._checkCopyright(text, node)
        self._checkTestReference(text, node)
        self._checkDocstring(text, node)


    def _checkCopyright(self, text, node):
        """
        Check whether the module has copyright header.

        @param text: codes of the module
        @param node: node of the module
        """
        for docstring in self.commentsCopyright:
            if docstring not in text:
                self.add_message('W9001', node=node)
                break


    def _checkTestReference(self, text, node):
        """
        Check whether a reference to its test module is contained.

        @param text: codes of the module
        @param node: node of the module
        """
        if not re.search(self.patternTestReference, text):
            self.add_message('W9002', node=node)


    def _checkDocstring(self, text, node):
        """
        Check whether docstring is contained.

        @param text: codes of the module
        @param node: node of the module
        """
        if not node.doc:
            self.add_message('W9003', node=node)
