import os
import sys

from logilab.astng import MANAGER

from twisted.trial import unittest

from twistedchecker.checkers.docstring import DocstringChecker


astng = MANAGER.astng_from_module_name


class FakeLinter(object):
    """
    A fake implementation of L{pylint.interfaces.ILinter} for
    collecting lint messages during tests.
    """
    def __init__(self):
        self.messages = []

    def add_message(self, *args, **kwargs):
        self.messages.append((args, kwargs))



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


    def test_missingModuleDocstring(self):
        """
        L{DocstringChecker} issues a warning for missing module
        docstrings.
        """
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring(
            'module', astng('example_docstrings_missing'))
        self.assertEquals(len(linter.messages), 1)


    def test_missingFunctionDocstring(self):
        """
        L{DocstringChecker} issues a warning for missing function
        docstrings.
        """
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring(
            'function', astng('example_docstrings_missing')['bar'])
        self.assertEquals(len(linter.messages), 1)


    def test_missingClassDocstring(self):
        """
        L{DocstringChecker} issues a warning for missing class
        docstrings.
        """
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring(
            'class', astng('example_docstrings_missing')['Foo'])
        self.assertEquals(len(linter.messages), 1)


    def test_missingMethodDocstring(self):
        """
        L{DocstringChecker} issues a warning for missing method
        docstrings.
        """
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring(
            'method', astng('example_docstrings_missing')['Foo']['bar'])
        self.assertEquals(len(linter.messages), 1)


    def test_allowInheritedDocstring(self):
        """
        Docstrings can be omitted if the method is contributing to a
        documented interface. In this case, the interface is defined
        locally.
        """
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring(
            'method',
            astng('example_docstrings_missing')['FooImplementation']['bar'])
        self.assertEquals(len(linter.messages), 0)


    def test_allowInheritedDocstringExternalAbsoluteInterface(self):
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
            astng('example_docstrings_missing')['FooImplementationExternalAbsoluteInterface']['bar'])
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
            astng('example_docstrings_missing')['FooImplementationExternalRelativeInterface']['bar'])

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
            astng('example_docstrings_missing')['FooImplementationExternalMultipleInterface']['bar'])
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
