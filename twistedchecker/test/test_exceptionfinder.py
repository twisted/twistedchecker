from twisted.trial import unittest

from twistedchecker.core.exceptionfinder import PatternFinder
from twistedchecker.core.exceptionfinder import findPatternsInFile
from twistedchecker.core.exceptionfinder import findAllExceptions
from twisted.python.filepath import FilePath



class ExceptionFinderTestCase(unittest.TestCase):
    """
    Test for twistedchecker.core.exceptionfinder.
    """

    def test_findPatternsInFile(self):
        """
        Test for twistedchecker.core.exceptionfinder.findPatternsInFile.
        """
        codes = """
obj, something = None, None

f = getattr(obj, "foo_" + something)
g = getattr(obj, "Bar_%s" % something)
getattr(obj, "baz_%s" % something)()
        """
        finder = PatternFinder()
        findPatternsInFile(codes, finder)
        self.assertEqual(finder.patternsFunc, {"foo_", "baz_"})
        self.assertEqual(finder.patternsClass, {"Bar_"})


    def test_findAllExceptions(self):
        """
        Test for twistedchecker.core.exceptionfinder.test_findAllExceptions.
        """
        pathTestFiles = createTestFiles(self.mktemp())
        patternsFunc, patternsClass = findAllExceptions(pathTestFiles)

        self.assertEqual(patternsFunc, {"foo_", "baz_"})
        self.assertEqual(patternsClass, {"Bar_"})



def createTestFiles(tempPath):
    """
    Create test files in file system.

    @tempPath: path of temp directory
    @return: path of test files
    """
    tempDir = FilePath(tempPath)
    tempDir.createDirectory()
    moduleInit = tempDir.child('__init__.py')
    moduleInit.setContent("")
    # A module declares exception for function names.
    moduleA = tempDir.child('a.py')
    moduleA.setContent("""
obj, something = None, None

func = getattr(obj, "foo_" + something)
getattr(obj, "baz_%s" % something)()
    """)
    # A module declares exception for class names.
    moduleB = tempDir.child('b.py')
    moduleB.setContent("""
obj, something = None, None

className = getattr(obj, "Bar_%s" % something)
    """)
    # A module contains invalid names.
    moduleTest = tempDir.child('test.py')
    moduleTest.setContent("""
# Not invalid names.
def foo_SOMETHING():
    pass

class Bar_SOMETHING():
    def baz_SOMETHING():
        pass

# Invalid names.
def a_SOMETHING():
    pass

class B_SOMETHING():
    def c_SOMETHING():
        pass
    """)
    return tempDir.path
