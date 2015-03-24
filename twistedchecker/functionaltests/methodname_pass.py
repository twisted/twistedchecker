# enable: C0103

class foo:

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

