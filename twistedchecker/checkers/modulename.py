import sys

from logilab import astng
from logilab.common.ureports import Table
from logilab.astng import are_exclusive

from pylint.interfaces import IASTNGChecker
from pylint.reporters import diff_string
from pylint.checkers import BaseChecker, EmptyReport

from twistedchecker.core.util import isTestModule, moduleNeedsTests

class ModuleNameChecker(BaseChecker):
    """
    A checker for checking module names.
    """
    msgs = {
     'W9301': ('Test modules should begin with test_',
               'Check if a test module begins with test_.'),
    }
    __implements__ = IASTNGChecker
    name = 'modulename'
    options = ()

    def visit_module(self, node):
        """
        A interface will be called when visiting a module.

        @param node: node of current module
        """
        modulename = node.name.split(".")[-1]
        if isTestModule(node.name) and moduleNeedsTests:
            self._checkTestModuleName(modulename, node)


    def _checkTestModuleName(self, modulename, node):
        """
        Check whether a test module have correct module name.
        The module name should begins with test_.

        @param modulename: a module name
        """
        if not modulename.startswith("test_"):
            self.add_message('W9301', node=node)
