# enable: W9301

# This is a test module,
# So its module name should starts with test_

from twisted.trial import unittest


class SubclassOfTestCase(unittest.TestCase):
    """
    A subclass of TestCase.
    """
    def test_something(self):
        """
        A test method.
        """
        pass
