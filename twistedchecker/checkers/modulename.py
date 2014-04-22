import re

from pylint.interfaces import IASTNGChecker
from pylint.checkers import BaseChecker

from twistedchecker.core.util import isTestModule


class ModuleNameChecker(BaseChecker):
    """
    A checker for checking module names.
    """
    msgs = {
     'W9301': ('Test modules should begin with test_',
               'Used when a test module begins with test_.'),
    }
    __implements__ = IASTNGChecker
    name = 'modulename'
    options = ()

    def moduleContainsTestCase(self, node):
        """
        Determine whether a module contains a subclass of TestCase.

        @param node: node of given module
        """
        patternTestCase = r"class\s+[a-zA-Z0-9]+\s*\(.*TestCase\)"
        return re.search(patternTestCase, node.file_stream.read()) \
               and True or False


    def visit_module(self, node):
        """
        A interface will be called when visiting a module.

        @param node: node of current module
        """
        modulename = node.name.split(".")[-1]
        if isTestModule(node.name) and self.moduleContainsTestCase(node):
            self._checkTestModuleName(modulename, node)


    def _checkTestModuleName(self, modulename, node):
        """
        Check whether a test module has correct module name.
        The module name should begins with test_.

        @param modulename: a module name
        """
        if not modulename.startswith("test_"):
            self.add_message('W9301', node=node)
