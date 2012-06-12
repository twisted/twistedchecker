# enable: W9301

# A test module begins with test_

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
