# enable: C9302,C9303

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


class SomeValidTests(object):
    """
    This test suite class contains only valid method named.
    """

    def _normalPrivateMethod(self):
        pass


    def normalMethod(self):
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
