from pylint.interfaces import IASTNGChecker
from pylint.checkers import BaseChecker
from logilab.astng.scoped_nodes import Class

from twistedchecker.core.util import isTestModule


class TestClassNameChecker(BaseChecker):
    """
    A checker for checking test class names.

    Test classes should be named FooTests, where Foo is the name
    of the component/feature being tested.
    """
    msgs = {
        'W9701': ('Test class names should end with Tests',
                  'Used for checking test class names.'),
    }
    __implements__ = IASTNGChecker
    name = 'testclassname'
    options = ()

    def visit_module(self, node):
        """
        An interface will be called when visiting a module.

        @param node: node of current module
        """
        if isTestModule(node.name):
            self._checkTestClassNames(node)


    def _isTestClass(self, klass):
        """
        Check whether a class is a test class. Here we assume that a
        test class is any class that contains one or more test_* or
        test* methods and inherits from TestCase.

        @param klass: A L{logilab.astng.scoped_nodes.Class} representing
            a class within the current node.
        @type klass: L{logilab.astng.scoped_nodes.Class}

        @return: A L{bool} representing whether the given class is a test
            class or not.
        @rtype: L{bool}
        """
        ancestors = [ancestor.name for ancestor in klass.ancestors()]
        methods = [method.name for method in klass.mymethods()]

        if 'TestCase' in ancestors:
            for method in methods:
                if method.startswith('test'):
                    return True
        return False


    def _checkTestClassNames(self, node):
        """
        Check whether test classes are named correctly. A test
        class name should end with Tests (for instance, FooTests).

        @param node: node of current module
        """
        objects = node.values()
        objects.sort(key=lambda obj: obj.lineno)
        for obj in objects:
            if isinstance(obj, Class):
                if self._isTestClass(obj) and not obj.name.endswith('Tests'):
                    self.add_message('W9701', line=obj.lineno)
