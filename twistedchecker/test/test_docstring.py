# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twistedchecker.checkers.docstring}
"""

from collections import namedtuple
import os
import sys

from logilab.astng.nodes import (
    CallFunc, Decorators, From, Import, Module, Name, TryExcept)
from logilab.astng.scoped_nodes import Function, Class

from twisted.trial import unittest

from twistedchecker.checkers.docstring import _closest, DocstringChecker



class RaisedArgs(Exception):
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs



# A container for the messages passed to FakeLinter.add_message
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
        Record calls to C{add_message}

        @see: L{pylint.interfaces.ILinter.add_message} for signature
            documentation.
        """
        self.messages.append(FakeLinterMessage(msg_id, line, node, args))



class DummyNode(object):
    """
    A dummy implementation of L{logilab.astng.bases.Statement}.

    Use as a dummy for certain scoped nodes eg C{Function}, C{Class},
    C{Module} etc.
    """
    def __init__(self, doc=None, parent=None, type=None):
        """
        Set the minimum required attributes on the dummy node.

        @param doc: A fake docstring to add to the node.
        @type doc: L{str}

        @param parent: A dummy parent node
        @type parent: mixed

        @param type: The name of the node type eg function, method,
            class, module.
        @type type: L{str}
        """
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
        nodes of any type with MISSING docstrings.
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


    def test_emptyDocstring(self):
        """
        L{DocstringChecker._check_docstring} issues a W9209 warning for
        nodes of any type with EMPTY docstrings.
        """
        nodeTypes = ('module', 'function', 'class', 'method')
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        for nodeType in nodeTypes:
            checker._check_docstring(nodeType, DummyNode(doc=''))

        self.assertEqual(
            ['W9209'] * len(nodeTypes),
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


    def _createMethodNode(self, methodName='baz', className='Foo',
                          decoratorName=None, decoratorArgs=()):
        """
        Return an L{astng} node of a dummy method wrapped in a dummy class
        with or without class decorators.

        @param methodName: The name of the dummy method
        @type methodName: L{str}

        @param className: The name of the dummy class
        @type className: L{str}

        @param decoratorName: The (optional) name of a dummy class
            decorator to be added to the dummy class. Default L{None}
            means no decorator.
        @type decoratorName: L{str} or L{None}

        @param decoratorArgs: A list of dummy arguments to be added to
            the class decorator.
        @type decoratorArgs: L{list} of L{str}

        @return: The dummy method node.
        @rtype: L{logilab.astng.nodes.Class}
        """
        if decoratorName is None:
            decorators = None
        else:
            decoratorNode = CallFunc()
            decoratorNode.func = Function(name=decoratorName, doc='')
            decoratorNode.args = []
            for n in decoratorArgs:
                argNameNode = Name()
                argNameNode.name = n
                decoratorNode.args.append(argNameNode)
            decorators = Decorators(nodes=[decoratorNode])

        parentNode = Class(name=className, doc='')
        parentNode.decorators = decorators
        childNode = Function(name=methodName, doc='')
        childNode.type = 'method'
        childNode.parent = parentNode
        self.assertTrue(childNode.is_method())
        return childNode


    def test_closest(self):
        """
        L{docstring._closest} locates the nearest ancestor class node.
        """
        childNode = self._createMethodNode(
            decoratorName=None)

        te = TryExcept()
        childNode.parent, te.parent = te, childNode.parent

        self.assertIdentical(te.parent, _closest(childNode, Class))


    def test_docstringCheckerClosest(self):
        """
        L{DocstringChecker._closest} is L{docstring._closest} by default
        """
        self.assertIdentical(_closest, DocstringChecker._closest)


    def test_docstringInheritedCallsClosestToFindNearestClass(self):
        """
        L{DocstringChecker._docstringInherited} calls _closest to locate
        the nearest ancestor Class node to check for decorators.
        """
        childNode = self._createMethodNode(
            decoratorName=None)

        checker = DocstringChecker(linter=None)
        def raisingClosest(*args, **kwargs):
            raise RaisedArgs(args, kwargs)
        self.patch(checker, '_closest', raisingClosest)

        e = self.assertRaises(
            RaisedArgs,
            checker._docstringInherited, childNode)
        self.assertEqual(
            ((childNode, Class), {}),
            (e.args, e.kwargs))


    def test_docstringInheritedInderectParentClassNoDecorators(self):
        """
        L{DocstringChecker._docstringInherited} returns L{False} if the
        supplied method C{node}'s closest class node does not have a decorators
        attribute, even when the method is in a try..except
        """
        childNode = self._createMethodNode(
            decoratorName=None)

        te = TryExcept()
        childNode.parent, te.parent = te, childNode.parent

        self.assertFalse(
            DocstringChecker(linter=None)._docstringInherited(childNode))


    def test_docstringInheritedEmptyDecorators(self):
        """
        L{DocstringChecker._docstringInherited} returns L{False} if the
        supplied method C{node}'s parent node has an empty decorators
        attribute.
        """
        childNode = self._createMethodNode(
            decoratorName=None)

        self.assertFalse(
            DocstringChecker(linter=None)._docstringInherited(childNode))


    def test_docstringInheritedWithOtherDecorators(self):
        """
        L{DocstringChecker._docstringInherited} returns L{False} if the
        supplied method C{node}'s parent class has no decorators named
        "implementer".
        XXX: fragile -- see comment in code.
        """
        childNode = self._createMethodNode(
            methodName='baz',
            decoratorName='FOOBAR')

        self.assertFalse(
            DocstringChecker(linter=None)._docstringInherited(childNode))


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
            # Return an empty class
            return Class(name=interfaceName, doc='')
        self.patch(checker, '_getInterface', fakeGetInterface)

        childNode = self._createMethodNode(
            methodName='foo',
            decoratorName='implementer',
            decoratorArgs=['Ignored1', 'Ignored2'])
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
            # Return a  class with a dummy baz method
            c = Class(name=interfaceName, doc='')
            c.locals['baz'] = object()
            return c
        self.patch(checker, '_getInterface', fakeGetInterface)

        childNode = self._createMethodNode(
            methodName='baz',
            decoratorName='implementer',
            decoratorArgs=['Ignored1'])

        result = checker._docstringInherited(childNode)

        self.assertTrue(result)


    def test_getInterfaceUndefinedUnqualifiedInterfaceName(self):
        """
        L{DocstringChecker._getInterface} raises KeyError if the supplied
        interface name is not found among the local variables of
        node's root module.
        """
        class DummyChild(object):
            locals = {}
            def root(self):
                return self

        e = self.assertRaises(
            KeyError,
            DocstringChecker(linter=None)._getInterface,
            node=DummyChild(), interfaceName='IFoo')
        self.assertEqual('IFoo', e.message)


    def test_getInterfaceUndefinedQualifiedInterfaceName(self):
        """
        If the supplied interfaceName is a qualified name, the first
        segment of the name is looked up in the node's root module.
        """
        class DummyChild(object):
            locals = {}
            def root(self):
                return self

        e = self.assertRaises(
            KeyError,
            DocstringChecker(linter=None)._getInterface,
            node=DummyChild(), interfaceName='foo.bar.IFoo')
        self.assertEqual('foo', e.message)


    def test_getInterfaceUnexpectedNodeType(self):
        """
        L{DocstringChecker._getInterface} raises AssertionError if the
        requested interface is not a local C{class} or imported using
        C{import}, C{import from}.
        """
        class DummyChild(object):
            # Return unhandled node type
            locals = dict(foo=[Function(name='foo', doc='')])
            def root(self):
                return self

        e = self.assertRaises(
            AssertionError,
            DocstringChecker(linter=None)._getInterface,
            node=DummyChild(), interfaceName='foo.IFoo')
        self.assertIn('Unexpected interfaceNode type.', e.message)


    def test_getInterfaceClassNode(self):
        """
        L{DocstringChecker._getInterface} returns a local interface as a
        Class node. (when I say "local interface" I meand one defined
        in the same module as the implementation class.)
        """
        dummyInterface = Class(name='IFoo', doc='')

        class DummyChild(object):
            # Return unhandled node type
            locals = dict(IFoo=[dummyInterface])
            def root(self):
                return self

        self.assertIdentical(
            dummyInterface,
            DocstringChecker(linter=None)._getInterface(
                node=DummyChild(), interfaceName='IFoo'))


    def test_getInterfaceImportNode(self):
        """
        If the interface is imported using a simple import statement
        L{DocstringChecker._getInterface} will call the C{import_node}
        method on the root module, supplying module name of the
        imported interface node as the argument.

        import foo.bar
        foo.bar.IFoo
        """
        dummyInterface = Import()

        class DummyChild(object):
            # Return unhandled node type
            locals = dict(foo=[dummyInterface])
            def root(self):
                return self
            def import_module(self, *args, **kwargs):
                raise RaisedArgs(args, kwargs)

        e = self.assertRaises(
            RaisedArgs,
            DocstringChecker(linter=None)._getInterface,
            node=DummyChild(), interfaceName='foo.bar.IFoo')
        self.assertEqual(
            (e.args, e.kwargs),
            (('foo.bar',), {}))


    def test_getInterfaceFromNode(self):
        """
        If the interface is imported using a import from statement
        L{DocstringChecker._getInterface} will call the C{import_node}
        method on the root module, supplying module name of the
        imported interface node as the argument.

        from foo import bar
        bar.IFoo
        """
        class DummyChild(object):
            # Return unhandled node type
            locals = dict(bar=[From(fromname='foo', names=[('bar', None)])])
            def root(self):
                return self
            def import_module(self, *args, **kwargs):
                raise RaisedArgs(args, kwargs)

        e = self.assertRaises(
            RaisedArgs,
            DocstringChecker(linter=None)._getInterface,
            node=DummyChild(), interfaceName='bar.IFoo')
        self.assertEqual(
            (e.args, e.kwargs),
            (('foo.bar',), {}))


    def test_getInterfaceNotFound(self):
        """
        L{DocstringChecker._getInterface} raises L{AssertionError} if the
        module returned by C{import_node} does not contain the
        interface classname.
        """
        class DummyChild(object):
            # Return unhandled node type
            locals = dict(bar=[From(fromname='foo', names=[('bar', None)])])
            def root(self):
                return self
            def import_module(self, *args, **kwargs):
                m = Module(name='bar', doc='')
                m.locals = dict()
                return m

        e = self.assertRaises(
            AssertionError,
            DocstringChecker(linter=None)._getInterface,
            node=DummyChild(), interfaceName='bar.IFoo')
        self.assertSubstring(
            "Interface not found. name: 'IFoo', module: ", e.message)


    def test_getInterfaceUnexpectedType(self):
        """
        L{DocstringChecker._getInterface} raises L{AssertionError} if the
        module returned by C{import_node} contains the interface
        classname but with type that is not Class.
        """
        class DummyChild(object):
            # Return unhandled node type
            locals = dict(bar=[From(fromname='foo', names=[('bar', None)])])
            def root(self):
                return self
            def import_module(self, *args, **kwargs):
                m = Module(name='bar', doc='')
                m.locals = dict(IFoo=[object()])
                return m

        e = self.assertRaises(
            AssertionError,
            DocstringChecker(linter=None)._getInterface,
            node=DummyChild(), interfaceName='bar.IFoo')
        self.assertSubstring(
            "Unexpected interface type. "
            "interfaceName: 'bar.IFoo', "
            "interface: <object object", e.message)


    def test_getInterfaceFound(self):
        """
        L{DocstringChecker._getInterface} returns the Class node
        representing imported interface.
        """
        dummyInterface = Class(name='IFoo', doc='')

        class DummyChild(object):
            # Return unhandled node type
            locals = dict(bar=[From(fromname='foo', names=[('bar', None)])])
            def root(self):
                return self
            def import_module(self, *args, **kwargs):
                m = Module(name='bar', doc='')
                m.locals = dict(IFoo=[dummyInterface])
                return m

        checker = DocstringChecker(linter=None)
        self.assertIdentical(
            dummyInterface,
            checker._getInterface(node=DummyChild(), interfaceName='bar.IFoo'))


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
