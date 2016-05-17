# enable: C9302

class BadMethodNames:
    """
    Methods should be in mixed case, with the first letter lower case,
    each word separated by having its first letter capitalized.
    """

    def CapitalCase(self):
        pass


    def ALLCAPITALCASE(self):
        pass


    def ssh_other_command(self):
        """
        Dispatched command with has no other similar command.

        The checker will consider this an error.
        """
        pass


    def publicMethod_name(self):
        """
        Method names should be fully in camel case.
        """
        pass


    def _privateMethods_not_all_camel(self):
        pass


    def __hiddenMethods_not_all_camel(self):
        pass


    def ___toPrivate(self):
        """
        Method can not start with 3 underscores.
        """

    def __reservedShortEnd_(self):
        pass


    def __reservedLongEnd___(self):
        pass


class SomeInvalidMixin(object):
    """
    Mixin with test methods.
    """

    def testLegacyMethod(self):
        """
        Legacy test method names should no longer be accepted.
        """
        pass


class SomeInvalidTests(object):
    """
    Test suite implementation.
    """

    def testLegacyMethod(self):
        """
        Legacy test method names should no longer be accepted.
        """
        pass


class GoodMethodNames:

    def test(self):
        pass


    def _test(self):
        pass


    def _testConnection(self):
        pass


    def _testPrivateConnection(self):
        pass


    def testPublicConnection(self):
        """
        This method name would have not been valid if this class is a
        test suite.
        """
        pass

    def _FOOBAR(self):
        pass


    def _normalPrivateMethod(self):
        pass


    def __hiddenMethod(self):
        pass


    def __reservedMethod__(self):
        pass


    def __reserved_method__(self):
        pass


    def ftp_COMMAND(self):
        """
        Dispatched command with at least another sibling.

        The checker will heuristically consider this a valid method.
        """
        pass


    def ftp_OTHER_COMMAND(self):
        pass


    def global_port_forwarding(self):
        """
        Dispatched with a sibling with lower case.
        """
        pass


    def global_cancel_port_forwarding(self):
        pass


    def test_SOME_THING(self):
        """
        In Twisted we have methods like render_POST, xmlrpc_SOMETHING and due
        to this test methods like test_SOME_THING or
        test_render_POSTSomething are valid.
        """
        pass


    def test_render_POSTSomething(self):
        pass
