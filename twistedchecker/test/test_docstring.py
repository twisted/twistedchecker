from collections import namedtuple
import os
import sys

from logilab.astng import MANAGER
from logilab.astng.nodes import CallFunc, Decorators, Name
from logilab.astng.scoped_nodes import Function, Class

from twisted.trial import unittest

from twistedchecker.checkers.docstring import DocstringChecker


# Shortened function name for convenience in tests.
astng = MANAGER.astng_from_module_name



FakeLinterMessage = namedtuple('FakeLinterMessage', 'msg_id line node args')



class FakeLinter(object):
    """
    A fake implementation of L{pylint.interfaces.ILinter} for
    collecting and verifying lint messages during tests.
    """
    def __init__(self):
        self.messages = []


    def add_message(self, msg_id, line=None, node=None, args=None):
        """

        """
        self.messages.append(FakeLinterMessage(msg_id, line, node, args))



class DummyNode(object):
    def __init__(self, doc=None, parent=None, type=None):
        self.doc = doc
        self.parent = parent
        self.type = type



class DocstringTestCase(unittest.TestCase):
    """
    Test for twistedchecker.checkers.docstring
    """

    def setUp(self):
        """
        Manipulate the Python import path so that the test module and
        its test interface module can be imported.
        """
        self.originalPath = sys.path[:]
        self.originalModules = sys.modules.copy()
        sys.path.append(os.path.dirname(__file__))


    def tearDown(self):
        """
        Return the import path and the imported modules to their
        original state.
        """
        sys.modules.clear()
        sys.modules.update(self.originalModules)
        sys.path[:] = self.originalPath


    def test_missingDocstring(self):
        """
        L{DocstringChecker._check_docstring} issues a W9208 warning for
        nodes of any type with missing docstrings.
        """
        nodeTypes = ('module', 'function', 'class', 'method')
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        for nodeType in nodeTypes:
            checker._check_docstring(nodeType, DummyNode(doc=None))

        self.assertEqual(
            ['W9208'] * len(nodeTypes),
            [m.msg_id for m in linter.messages]
        )


    def test_checkDocstringSkipNestedFunctions(self):
        """
        L{DocstringChecker._check_docstring} does not issue any warnings
        if the undocumented node is a nested in a function.
        """
        nodeTypes = ('module', 'function', 'class', 'method')
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        for nodeType in nodeTypes:
            checker._check_docstring(
                nodeType,
                DummyNode(doc=None,
                          parent=Function(name='foo', doc=None)))

        self.assertEqual(
            [],
            linter.messages
        )


    def test_checkDocstringSkipDocStringInherited(self):
        """
        L{DocstringChecker._check_docstring} does not issue any warnings
        if the undocumented node implements a documented interface.
        L{DocstringChecker._docstringInherited} is called with the
        node to check for a documented interface.
        """
        nodeTypes = ('module', 'function', 'class', 'method')
        nodes = [DummyNode() for nodeType in nodeTypes]
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)

        calls = []
        def fakeDocstringInherited(node):
            calls.append(node)
            return True
        self.patch(checker, '_docstringInherited', fakeDocstringInherited)

        for nodeType, node in zip(nodeType, nodes):
            checker._check_docstring(nodeType, node)

        self.assertEquals(
            (nodes, []),
            (calls, linter.messages))


    def test_docstringInheritedNonFunction(self):
        """
        L{DocstringChecker._docstringInherited} returns L{False} if the
        supplied C{node} is not a function.
        """
        self.assertFalse(
            DocstringChecker(linter=None)._docstringInherited(node=object()))


    def test_docstringInheritedNonMethod(self):
        """
        L{DocstringChecker._docstringInherited} returns L{False} if the
        supplied Function C{node} is not a method.
        """
        node = Function(name='foo', doc='')
        node.type = 'function'
        self.assertFalse(node.is_method())

        self.assertFalse(
            DocstringChecker(linter=None)._docstringInherited(node))


    def test_docstringInheritedNoDecorators(self):
        """
        L{DocstringChecker._docstringInherited} returns L{False} if the
        supplied method C{node}'s parent class has no decorators.
        """
        parentNode = Class(name='Foo', doc='')
        parentNode.decorators = None
        childNode = Function(name='foo', doc='')
        childNode.type = 'method'
        childNode.parent = parentNode
        self.assertTrue(childNode.is_method())

        self.assertFalse(
            DocstringChecker(linter=None)._docstringInherited(childNode))


    def test_docstringInheritedWithOtherDecorators(self):
        """
        L{DocstringChecker._docstringInherited} returns L{False} if the
        supplied method C{node}'s parent class has no decorators named
        "implementer".
        XXX: fragile -- see comment in code.
        """
        decorator = CallFunc()
        decorator.func = Function(name='FOOBAR', doc='')

        parentNode = Class(name='Foo', doc='')
        parentNode.decorators = Decorators(nodes=[decorator])
        childNode = Function(name='foo', doc='')
        childNode.type = 'method'
        childNode.parent = parentNode
        self.assertTrue(childNode.is_method())

        self.assertFalse(
            DocstringChecker(linter=None)._docstringInherited(childNode))


    def _createMethodNode(self, methodName='baz', interfaceNames=None):
        if interfaceNames is None:
            decorators = None
        else:
            decoratorNode = CallFunc()
            decoratorNode.func = Function(name='implementer', doc='')
            decoratorNode.args = []
            for n in interfaceNames:
                interfaceNameNode = Name()
                interfaceNameNode.name = n
                decoratorNode.args.append(interfaceNameNode)
            decorators = Decorators(nodes=[decoratorNode])

        parentNode = Class(name='Foo', doc='')
        parentNode.decorators = decorators
        childNode = Function(name=methodName, doc='')
        childNode.type = 'method'
        childNode.parent = parentNode
        self.assertTrue(childNode.is_method())
        return childNode


    def test_docstringInheritedWithMultipleNonMatchingDecoratorArguments(self):
        """
        L{DocstringChecker._docstringInherited} calls
        L{DocstringChecker._getInterface} for each of the interface
        names that were passed to the implementer decorator. The node
        and the interface name are supplied as positional arguments.

        If none of the named interfaces contain the node name return
        False.
        """

        checker = DocstringChecker(linter=None)

        nodes = []
        interfaceNames = []
        def fakeGetInterface(node, interfaceName):
            nodes.append(node)
            interfaceNames.append(interfaceName)
            # return an empty class
            return Class(name=interfaceName, doc='')
        self.patch(checker, '_getInterface', fakeGetInterface)

        childNode = self._createMethodNode(
            methodName='foo',
            interfaceNames=['Ignored1', 'Ignored2'])
        result = checker._docstringInherited(childNode)

        self.assertEqual(
            ([childNode, childNode], ['Ignored1', 'Ignored2'], False),
            (nodes, interfaceNames, result)
        )



    def test_docstringInheritedWithMatchingDecoratorArguments(self):
        """
        If any of the named interfaces returned by _getInterface contain
        the node name return True.
        """

        checker = DocstringChecker(linter=None)

        def fakeGetInterface(node, interfaceName):
            # return a  class with a dummy baz method
            c = Class(name=interfaceName, doc='')
            c.locals['baz'] = object()
            return c
        self.patch(checker, '_getInterface', fakeGetInterface)

        childNode = self._createMethodNode(
            methodName='baz',
            interfaceNames=['Ignored1'])

        result = checker._docstringInherited(childNode)

        self.assertTrue(result)


    def test_docstringInheritedLocalInterface(self):
        """
        L{DocstringChecker._docstringInherited} returns L{True} if the
        supplied C{node} is found to implement a local interface.
        """
        checker = DocstringChecker(linter=None)
        module = astng('examples.example_docstrings_missing')
        self.assertTrue(
            checker._docstringInherited(module['FooImplementation']['bar']))


    def test_allowInheritedDocstringExternalAbsoluteInterface(self):
        """
        L{DocstringChecker._docstringInherited} returns L{True} if the
        supplied C{node} is found to implement a local interface.
        """
        checker = DocstringChecker(linter=None)
        module = astng('examples.example_docstrings_missing')
        self.assertTrue(
            checker._docstringInherited(module['FooImplementation']['bar']))


        """
        Docstrings can be omitted if the method is contributing to a
        documented interface. In this case an interface that has been
        imported from another module and is referenced using its
        absolute path.
        """
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring(
            'method',
            astng('examples.example_docstrings_missing')['FooImplementationExternalAbsoluteInterface']['bar'])
        self.assertEquals(len(linter.messages), 0)


    def test_allowInheritedDocstringExternalRelativeInterface(self):
        """
        Docstrings can be omitted if the method is contributing to a
        documented interface. In this case the interface is referenced
        using a local relative import path.
        """
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring(
            'method',
            astng('examples.example_docstrings_missing')['FooImplementationExternalRelativeInterface']['bar'])

        self.assertEquals(len(linter.messages), 0)


    def test_allowInheritedDocstringExternalMultipleInterface(self):
        """
        Docstrings can be omitted if the method is contributing to a
        documented interface. Here the class implements multiple
        interfaces.
        """
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring(
            'method',
            astng('examples.example_docstrings_missing')['FooImplementationExternalMultipleInterface']['bar'])
        self.assertEquals(len(linter.messages), 0)


    def test_emptyModuleDocstring(self):
        """
        L{DocstringChecker} issues a warning for empty module
        docstrings.
        """
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring(
            'module', astng('examples.example_docstrings_empty'))
        self.assertEquals(len(linter.messages), 1)


    def test_getLineIndent(self):
        """
        Test of twistedchecker.checkers.docstring._getLineIndent.
        """
        checker = DocstringChecker()
        indentNoSpace = checker._getLineIndent("foo")
        indentTwoSpaces = checker._getLineIndent("  foo")
        indentFourSpaces = checker._getLineIndent("    foo")
        self.assertEqual(indentNoSpace, 0)
        self.assertEqual(indentTwoSpaces, 2)
        self.assertEqual(indentFourSpaces, 4)
