import re

from pylint.interfaces import IASTNGChecker
from pylint.checkers import BaseChecker

from twistedchecker.core.util import isTestModule, moduleNeedsTests


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
    }
    __implements__ = IASTNGChecker
    name = 'header'
    options = ()
    commentsCopyright = (r"# Copyright \(c\) Twisted Matrix Laboratories\.",
                         r"# See LICENSE for details\.")
    patternTestReference = (r"# -\*- test-case-name:"
                            r" (([a-z_][a-z0-9_]*)\.)*[a-z_][a-z0-9_]* -\*-")


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
        if not isTestModule(node.name) and moduleNeedsTests:
            self._checkTestReference(text, node)


    def _checkCopyright(self, text, node):
        """
        Check whether the module has copyright header.

        @param text: codes of the module
        @param node: node of the module
        """
        if not re.search(r"%s\s*\n\s*%s" % self.commentsCopyright, text):
            self.add_message('W9001', node=node)


    def _checkTestReference(self, text, node):
        """
        Check whether a reference to its test module is contained.

        @param text: codes of the module
        @param node: node of the module
        """
        if '.test.' in node.name or '.test_' in node.name:
            # Test packages or test modules don't need references to tests.
            return

        if not re.search(self.patternTestReference, text):
            self.add_message('W9002', node=node)
