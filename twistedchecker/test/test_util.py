from twisted.trial import unittest

from twistedchecker.core.util import isTestModule, moduleNeedsTests



class UtilTestCase(unittest.TestCase):
    """
    Test for twistedchecker.core.util
    """

    def test_isTestMoudle(self):
        """
        isTestMoudle returns True if the given module name has '.test.' in it.
        """
        self.assertTrue(isTestModule("twisted.test.test_dict"))
        self.assertTrue(isTestModule("twisted.python.test.test_util"))
        self.assertFalse(isTestModule("twisted.test.iosim"))
        self.assertFalse(isTestModule("twisted.python.hook"))


    def test_moduleNeedsTests(self):
        """
        moduleNeedsTests returns true
        if the module name starts with an underscore.
        """
        self.assertFalse(moduleNeedsTests("twisted.python.__init__"))
        self.assertFalse(moduleNeedsTests("twisted.python._release"))
        self.assertTrue(moduleNeedsTests("twisted.python.hook"))
