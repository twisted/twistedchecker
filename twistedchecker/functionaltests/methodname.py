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
        Method names should be fully in camel case.
        """
        pass


    def _privateMethods_not_all_camel(self):
        pass


    def __hiddenMethods_not_all_camel(self):
        pass



class GoodMethodNames:

    def test(self):
        pass


    def _test(self):
        pass


    def _testMethod(self):
        pass


    def get_testMethod(self):
        pass


    def _FOOBAR(self):
        pass


    def test_SOME_THING(self):
        """
        In Twisted we have methods like render_POST, xmlrpc_SOMETHING and due to this
        test methods like test_render_POSTSomething are valid.
        """
        pass


    def test_render_POSTSomething(self):
        pass


    def _normalPrivateMethod(self):
        pass


    def __hiddenMethod(self):
        pass

