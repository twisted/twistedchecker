# enable: C0103

class foo:
    """
    Methods should be in mixed case, with the first letter lower case,
    each word separated by having its first letter capitalized.
    """

    def TestMethod(self):
        pass


    def Test(self):
        pass


    def TESTMETHOD(self):
        pass


    def testMethod_of_foo(self):
        pass


    def test_SOME_THING(self):
        """
        Test method should not use underscores.
        """
        pass


    def testLegacyMethod(self):
        """
        Legacy test method names should no longer be accepted.
        """
        pass


    def some_method(self):
        """
        Method names should be in camel case.
        """
        pass


    def someMethod_name(self):
        """
        Method names should be in camel case.
        """
        pass
