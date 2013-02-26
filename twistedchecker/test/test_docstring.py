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
            methods[method.name] = method
        self.methods = methods



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

        self.module = AstngTestModule(filepath, modname)


    def test_allowInheritedDocstring(self):
        """
        docstrings can be omitted if the method is contributing to a
        documented interface.
        """
        testclass = self.module.classes['FooImplementation']
        testmethod = testclass.methods['test_allowInheritedDocstring']
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        checker._check_docstring('method', testmethod)
        self.assertEquals(len(linter.messages), 0)


    def test_missingModuleDocstring(self):

        pass

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
