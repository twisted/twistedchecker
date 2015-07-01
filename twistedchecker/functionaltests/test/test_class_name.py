# enable: W9701

# A test class name should end with Tests (for instance, FooTests).
# Here we are assuming that a test class is any class that contains
# one or more test_* methods.

from twisted.trial import unittest


class SpecializedTestCaseSubclass(unittest.TestCase):
    """
    A specialized TestCase subclass that test classes can
    inherit from. Note that even though this class inherits
    from TestCase, this class should not be checked by the
    checker, as this class does not contain a test_* method.
    """
    def doSomething(self):
        """
        Some method.
        """
        pass


class SomeTestMixin(object):
    """
    A mixin which does nothing.
    """

    def testLegacyName(self):
        """
        A test with old naming convention.
        """

#
# Bad examples
#
class SomethingTestCase(unittest.TestCase):
    """
    An incorrectly named test class.
    """
    def test_something(self):
        """
        A test method.
        """
        pass



class SomethingElseTest(unittest.TestCase, SomeTestMixin):
    """
    Another incorrectly named test class.
    """
    def test_somethingElse(self):
        """
        A test method.
        """
        pass



class TestFoo(SpecializedTestCaseSubclass):
    """
    One more incorrectly named test class.
    """
    def test_foo(self):
        """
        A test method.
        """
        pass



class LegacyTestCase(unittest.TestCase):
    """
    An incorrectly named test class.
    """
    def testSomething(self):
        """
        A test method with old naming convention.
        """


#
# Good examples
#
class SampleTestMixin(object):
    """
    A sample mixin with additional assertion helpers.
    """
    def assertSomething(self):
        """
        An assertion helper.
        """
        pass

    def test_someTest(self):
        """
        Test from mixin.
        """
        pass



class SomethingTests(unittest.TestCase):
    """
    A correctly named test class.
    """
    def test_something(self):
        """
        A test method.
        """



class SomethingElseTests(unittest.TestCase, SampleTestMixin):
    """
    Another correctly named test class.
    """
    def test_somethingElse(self):
        """
        A test method.
        """



class FooTests(SpecializedTestCaseSubclass):
    """
    One more correctly named test class.
    """
    def test_foo(self):
        """
        A test method.
        """



class LegacyTests(SpecializedTestCaseSubclass):
    """
    One more correctly named with test methods after older convention.
    """
    def testLegacyName(self):
        """
        A test method.
        """
