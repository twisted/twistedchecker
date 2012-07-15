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
