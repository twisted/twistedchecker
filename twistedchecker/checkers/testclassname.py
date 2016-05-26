import operator

from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker
from astroid.scoped_nodes import ClassDef

from twistedchecker.core.util import isTestModule


class TestClassNameChecker(BaseChecker):
    """
    A checker for checking test class names.

    Test classes should be named FooTests, where Foo is the name
    of the component/feature being tested.
    """
    msgs = {
        'W9701': ('Test class names should end with Tests',
                  'Used for checking test class names.',
                  'test-class-end-with-Tests'),
    }
    __implements__ = IAstroidChecker
    name = 'testclassname'
    options = ()

    def visit_module(self, node):
        """
        Called when the AST checker visits a module.

        @param node: node of current module
        """
        if not isTestModule(node.name):
            return
        objects = list(node.values())
        objects.sort(key=operator.attrgetter('lineno'))
        for obj in objects:
            if (isinstance(obj, ClassDef) and self._isTestClass(obj) and
                    not obj.name.endswith('Tests')):
                self.add_message('W9701', line=obj.lineno, node=obj)


    def _isTestClass(self, klass):
        """
        Check whether a class is a test class. Here we assume that a
        test class is any class that contains one or more test_* or
        test* methods and inherits from TestCase.

        @param klass: Class to be checked for whether it is a test class.
        @type klass: L{logilab.astng.scoped_nodes.Class}

        @return: C{True} if the given class is a test class, C{False}
            otherwise.
        @rtype: L{bool}
        """
        ancestors = [ancestor.name for ancestor in klass.ancestors()]
        methods = [method.name for method in klass.mymethods()]

        if 'TestCase' not in ancestors:
            return False

        for method in methods:
            if method.startswith('test'):
                return True
        return False
