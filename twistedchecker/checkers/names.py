"""
Checker for naming convention.
"""
import re

from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker

from twistedchecker.core.util import isTestModule


class TwistedNamesChecker(BaseChecker):
    """
    A checker for checking Twisted naming convention.
    """
    msgs = {
        'W9301': ('Test modules should begin with test_',
                  'Used when a test module begins with test_.',
                  'testmodule-not-beginning-with-test'),
        'C9302': ('Method name is invalid',
                  'Used when a method has invalid name.',
                  'invalid-method-name'),
        'C9303': ('Test method name is invalid',
                  'Used when a test method has invalid name.',
                  'invalid-test-method-name'),
    }
    __implements__ = IAstroidChecker
    name = 'modulename'
    options = ()

    def moduleContainsTestCase(self, node):
        """
        Determine whether a module contains a subclass of TestCase.

        @param node: node of given module
        """
        patternTestCase = br"class\s+[a-zA-Z0-9]+\s*\(.*TestCase\)"
        with node.stream() as stream:
            moduleRaw = stream.read()

        return re.search(patternTestCase, moduleRaw) and True or False


    def visit_module(self, node):
        """
        A interface will be called when visiting a module.

        @param node: node of current module
        """
        modulename = node.name.split(".")[-1]
        if isTestModule(node.name) and self.moduleContainsTestCase(node):
            self._checkTestModuleName(modulename, node)


    def visit_functiondef(self, node):
        """
        A interface will be called when visiting a function or a method.

        @param node: the current node
        """
        if not node.is_method():
            # We only check methods.
            return

        name = node.name

        if isTestModule(node.root().name):
            if name.startswith('test'):
                if not name.startswith('test_'):
                    self.add_message('C9303', node=node)
                    return
                else:
                    # Test names start with 'test_NAME' and can be like
                    # test_SOME_NAME or test_render_SomeCondition.
                    return

        if name[0].isupper():
            self.add_message('C9302', node=node)
            return

        if name.startswith('___'):
            self.add_message('C9302', node=node)
            return

        if name.endswith('___'):
            self.add_message('C9302', node=node)
            return

        if name.startswith('__'):
            if name.endswith('___'):
                # To many trailing underscores.
                self.add_message('C9302', node=node)
                return
            if name.endswith('_') and not name.endswith('__'):
                # To few trailing underscored
                self.add_message('C9302', node=node)
                return
            if name.endswith('__'):
                # This is a reserved name and we don't do any checks on it.
                return
            name = name[2:-2]

        if name.startswith('_'):
            name = name[1:]

        if name.endswith('_'):
            self.add_message('C9302', node=node)
            return

        if '_' in name:
            # This has a underscore in the main name.
            prefix = self._getMethodNamePrefix(node)
            if prefix:
                # There are other names with same prefix so this should be
                # a dispatched method.
                return

            self.add_message('C9302', node=node)
            return


        if isTestModule(node.name) and self.moduleContainsTestCase(node):
            self._checkTestMethodName(node)

    def _getMethodNamePrefix(self, node):
        """
        Return the prefix of this method based on sibling methods.

        @param node: the current node
        """
        targetName = node.name
        for sibling in node.parent.nodes_of_class(type(node)):
            if sibling is node:
                # We are on the same node in parent so we skip it.
                continue
            prefix = self._getCommonStart(targetName, sibling.name)
            if not prefix.rstrip('_'):
                # We ignore prefixes which are just underscores.
                continue
            return prefix

        return ''


    def _getCommonStart(self, left, right):
        """
        Return the common prefix of the 2 strings.

        @param left: one string
        @param right: another string
        """
        prefix = []
        for a, b in zip(left, right):
            if a == b:
                prefix.append(a)
            else:
                break

        return ''.join(prefix)


    def _checkTestModuleName(self, modulename, node):
        """
        Check whether a test module has correct module name.
        The module name should begins with test_.

        @param modulename: a module name
        """
        if not modulename.startswith("test_"):
            self.add_message('W9301', node=node)


    def _checkTestMethodName(self, modulename, node):
        """
        Check whether a test method has correct module name.

        @param modulename: a module name
        """
        if not modulename.startswith("test_"):
            self.add_message('W9301', node=node)
