import sys
import os
import StringIO

from logilab.astng import MANAGER, nodes, ASTNGBuildingException

from twisted.trial import unittest

from twistedchecker.checkers.docstring import DocstringChecker


class FakeLinter(object):
    def __init__(self):
        self.messages = []

    def add_message(self, *args, **kwargs):
        self.messages.append((args, kwargs))


class DocstringTestCase(unittest.TestCase):
    """
    Test for twistedchecker.checkers.docstring
    """

    def setUp(self):
        filepath = '/home/richard/projects/TwistedChecker/branches/inherited-interface-documentation-1132540/twistedchecker/functionaltests/docstring_pass.py'
        modname = 'twistedchecker.functionaltests.docstring_pass'
        astng = MANAGER.astng_from_file(filepath, modname, source=True)
        classes = {}
        for child in astng.get_children():
            if isinstance(child, nodes.Class):
                classes[child.name] = child
#        import pdb;pdb.set_trace()
        self._classes = classes


    def test_allowInheritedDocstring(self):
        """
        docstrings can be omitted if the method is contributing to a
        documented interface.
        """
        linter = FakeLinter()
        checker = DocstringChecker(linter=linter)
        for meth in self._classes['FooImplementation'].methods():
            if meth.name == 'test_allowInheritedDocstring':
                break
        else:
            self.fail('method not found')
        checker._check_docstring('method', meth)

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
