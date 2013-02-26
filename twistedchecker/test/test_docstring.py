from logilab.astng import MANAGER, nodes

from twisted.trial import unittest

from twistedchecker.checkers.docstring import DocstringChecker



class FakeLinter(object):
    def __init__(self):
        self.messages = []

    def add_message(self, *args, **kwargs):
        self.messages.append((args, kwargs))



class AstngTestModule(object):
    def __init__(self, filepath, modname):
        astng = MANAGER.astng_from_file(filepath, modname, source=True)
        self.node = astng
        classes = {}
        for child in astng.get_children():
            if isinstance(child, nodes.Class):
                classes[child.name] = AstngTestClass(child)
        self.classes = classes



class AstngTestClass(object):
    def __init__(self, node):
        self.node = node

        methods = {}
        for method in node.methods():
            methods[method.name] = AstngTestMethod(method)
        self.methods = methods



class AstngTestMethod(object):
    def __init__(self, node):
        self.node = node



class DocstringTestCase(unittest.TestCase):
    """
    Test for twistedchecker.checkers.docstring
    """

    def setUp(self):
        filepath = (
            '/home/richard/projects/TwistedChecker'
            '/branches/inherited-interface-documentation-1132540'
            '/twistedchecker/functionaltests/docstring_pass.py')

        modname = 'twistedchecker.functionaltests.docstring_pass'

        self.testmodule = AstngTestModule(filepath, modname)


    def test_missingModuleDocstring(self):
        """
        L{DocstringChecker} issues a warning for empty or missing
        module docstrings.
        """
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring('module', self.testmodule.node)
        self.assertEquals(len(linter.messages), 1)


    def test_missingClassDocstring(self):
        """
        L{DocstringChecker} issues a warning for empty or missing
        class docstrings.
        """
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring('class', self.testmodule.classes['FooImplementation'].node)
        self.assertEquals(len(linter.messages), 1)


    def test_allowInheritedDocstring(self):
        """
        Docstrings can be omitted if the method is contributing to a
        documented interface.
        """
        testclass = self.testmodule.classes['FooImplementation']
        testmethod = testclass.methods['test_allowInheritedDocstring'].node
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
