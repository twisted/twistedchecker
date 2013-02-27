import os
import sys

from logilab.astng import MANAGER, nodes

from twisted.trial import unittest

from twistedchecker.checkers.docstring import DocstringChecker



class FakeLinter(object):
    def __init__(self):
        self.messages = []

    def add_message(self, *args, **kwargs):
        self.messages.append((args, kwargs))



class AstngTestModule(object):
    filepath = 'example_docstrings_missing.py'
    modname = 'example_docstrings_missing'

    def __init__(self):
        testdir = os.path.dirname(__file__)
        astng = MANAGER.astng_from_file(
            os.path.join(testdir, self.filepath), self.modname, source=True)
        self.node = astng

        classes = {}
        functions = {}
        for child in astng.get_children():
            if isinstance(child, nodes.Class):
                classes[child.name] = AstngTestClass(child)
            if isinstance(child, nodes.Function):
                functions[child.name] = AstngTestFunction(child)

        self.functions = functions
        self.classes = classes



class AstngTestClass(object):
    def __init__(self, node):
        self.node = node

        methods = {}
        for method in node.methods():
            methods[method.name] = AstngTestFunction(method)
        self.methods = methods



class AstngTestFunction(object):
    def __init__(self, node):
        self.node = node



class DocstringTestCase(unittest.TestCase):
    """
    Test for twistedchecker.checkers.docstring
    """

    def setUp(self):
        self.originalPath = sys.path[:]
        self.originalModules = sys.modules.copy()
        sys.path.append(os.path.dirname(__file__))


    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self.originalModules)
        sys.path[:] = self.originalPath


    def test_missingModuleDocstring(self):
        """
        L{DocstringChecker} issues a warning for empty or missing
        module docstrings.
        """
        testmodule = AstngTestModule('example_docstrings_missing')
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring('module', testmodule.node)
        self.assertEquals(len(linter.messages), 1)


    def test_missingFunctionDocstring(self):
        """
        L{DocstringChecker} issues a warning for empty or missing
        function docstrings.
        """
        testmodule = AstngTestModule('example_docstrings_missing.bar')
        testfunc = testmodule.functions['bar']
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring('function', testfunc.node)
        self.assertEquals(len(linter.messages), 1)


    def test_missingClassDocstring(self):
        """
        L{DocstringChecker} issues a warning for empty or missing
        class docstrings.
        """
        testmodule = AstngTestModule()
        testclass = testmodule.classes['Foo']
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring('class', testclass.node)
        self.assertEquals(len(linter.messages), 1)


    def test_missingMethodDocstring(self):
        """
        L{DocstringChecker} issues a warning for empty or missing
        method docstrings.
        """
        testmodule = AstngTestModule()
        testclass = testmodule.classes['Foo']
        testmethod = testclass.methods['bar']
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring('method', testmethod.node)
        self.assertEquals(len(linter.messages), 1)


    def test_allowInheritedDocstring(self):
        """
        Docstrings can be omitted if the method is contributing to a
        documented interface.
        """
        testmodule = AstngTestModule()
        testclass = testmodule.classes['FooImplementation']
        testmethod = testclass.methods['bar'].node
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring('method', testmethod)
        self.assertEquals(len(linter.messages), 0)


    def test_allowInheritedDocstringExternal(self):
        """
        Docstrings can be omitted if the method is contributing to a
        documented interface. In this case an interface that has been
        imported from another module.
        """
        testmodule = AstngTestModule()
        testclass = testmodule.classes['FooImplementationExternal']
        testmethod = testclass.methods['bar'].node
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring('method', testmethod)
        self.assertEquals(len(linter.messages), 0)


    def test_allowInheritedDocstringExternal2(self):
        """
        Docstrings can be omitted if the method is contributing to a
        documented interface. In this case an interface that has been
        imported from another module.
        """
        testmodule = AstngTestModule()
        testclass = testmodule.classes['FooImplementationExternal2']
        testmethod = testclass.methods['bar'].node
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring('method', testmethod)
        self.assertEquals(len(linter.messages), 0)


    def test_allowInheritedDocstringExternal3(self):
        """
        Docstrings can be omitted if the method is contributing to a
        documented interface. Here the class implements multiple
        interfaces.
        """
        testmodule = AstngTestModule()
        testclass = testmodule.classes['FooImplementationExternal3']
        testmethod = testclass.methods['bar'].node
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring('method', testmethod)
        self.assertEquals(len(linter.messages), 0)


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
