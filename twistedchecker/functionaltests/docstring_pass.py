# enable: W9201,W9202,W9203,W9204,W9205,W9206,W9207,W9208,W9209
# -*- test-case-name: twistedchecker.test.test_functionaltests.FunctionalTests.test_twistedchecker_functionaltests_docstring_pass -*-
"""
A docstring with a wrong indentation.
Docstring should have consistent indentations.
"""

from elsewhere import aliasForProperty

class foo:
    """
    The opening/closing of docstring should be on a line by themselves.
    """

    def a(self):
        """
        A docstring with a correct indentation.
        """
        pass


    def b(self, argument1):
        """
        This docstring should contain epytext markups of argument1.

        @param argument1: an argument
        @type argument1: C{int}
        """
        pass


    def c(self):
        """
        This docstring should contain a @return and @rtype markup.

        @return: return 1
        @rtype: C{int}
        """
        return 1


    def d(self, a):
        """
        There should be a blank line before epytext markups.

        @param a: a argument
        @type a: C{int}
        @return: return a
        @rtype: C{int}
        """
        return a


    def e(self):
        """
        A method contains a function k().
        No warning should be generated
        """
        def k():
            pass


    @property
    def someProperty(self):
        """
        Getter properties don't need return docstring.
        """
        return True


    @someProperty.setter
    def someProperty(self, value):
        """
        Setter properties don't need to document their value.
        """

    @property
    def otherProperty(self):
        """
        Getter properties used the test that setter don't need a docstring.
        """
        return True


    @otherProperty.setter
    def otherProperty(self, value):
        # Setter don't need a docstring as most of the time is a duplicate of
        # the getter docstring.
        pass


    @aliasForProperty.setter
    def decorated(self):
        # If we have a decorator which *might* be a property, but is imported
        # from elsewhere (somewhere that pylint's parser can't see) then we
        # also don't need a docstring for its setter.
        pass


    def f(self):
        """
        A method returns nothing.
        """
        return


    def test_someTest(self):
        """
        Test methods in trial should not document their return value.
        """
        return 'deferred'



class Bar(object):
    """
    A cvar is recognized as being the start of epytext markup.

    @cvar foo: bar baz
    @type foo: bax
    """

    def a(self):
        """
        A raises field is recognized as being the start of epytext markup.

        @raises FoobarException: An exception.
        @returns: C{int}
        """

    def b(self):
        """
        A raise (because we are inconsistent about stuff) should also be
        recognized as the start of epytext markup.

        @raise BarException: Another exception.
        @returns: C{int}
        """
        def callback(result):
            pass



def topLevel():
    """
    A top-level function.
    """
    class Inner(object):
        def innerInner(self):
            pass



class Baz(object):
    """
    An ivar is recognized as being the start of epytext markup.

    @ivar foo: bar baz
    @type foo: bax
    """
