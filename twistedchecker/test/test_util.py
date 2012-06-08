import sys
import os
import StringIO

from twisted.trial import unittest

from twistedchecker.core.util import isTestModule, isSpecialModule


class UtilTestCase(unittest.TestCase):
    """
    Test for twistedchecker.core.util
    """

    def test_isTestMoudle(self):
        """
        Test of twistedchecker.core.util.isTestModule.
        """
        self.assertTrue(isTestModule("twisted.test.test_dict"))
        self.assertTrue(isTestModule("twisted.python.test.test_util"))
        self.assertFalse(isTestModule("twisted.python.hook"))


    def test_isSpecialModule(self):
        """
        Test of twistedchecker.core.util.isSpecialModule
        """
        self.assertTrue(isSpecialModule("twisted.python.__init__"))
        self.assertTrue(isSpecialModule("twisted.python._release"))
        self.assertFalse(isSpecialModule("twisted.python.hook"))
