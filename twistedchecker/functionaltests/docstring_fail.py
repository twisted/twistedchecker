# enable: W9201,W9202,W9203,W9204,W9205,W9206,W9207,W9208,W9209
"""
  A docstring with a wrong indentation.
  Docstring should have consistent indentations.
"""

class foo:
    '''The opening/closing of docstring should be on a line by themselves'''

    def a(self):
       """
         A docstring with a wrong indentation.
         """
       pass


    def b(self, argument1):
        """
        This docstring should contain epytext markups of argument1.
        """
        pass


    def c(self, argument1):
        """
        This docstring should contain a @param markup of argument1.

        @type argument1: C{str}
        """
        pass


    def d(self, _argument1):
        """
        This docstring should contain a @type markup of _argument1.

        @param _argument1: a argument
        """
        pass


    def e(self):
        """
        This docstring should contain a @return and @rtype markup.
        """
        return 1


    def f(self):
        """
        This docstring should contain a @return markup.

        @rtype: C{int}
        """
        return 1


    def g(self):
        """
        This docstring should contain a @rtype markup.

        @return: just return 1
        """
        return 1


    def h(self, a):
        """
        There should be a blank line before epytext markups
        @param a: a argument
        @type a: C{int}
        @return: return a
        @rtype: C{int}
        """
        return a


    def i(self):
        '''
            A docstring begins with single quotes,
            and have wrong indentation.
        '''
        pass


    def aCrazyMethod(this, self):
        """
        This is an example method using 'this' as a replacement of 'self'.
        This docstring should contain epytext for the parameter 'self'.
        By the way, this example will cause a fatal error E0213 in pylint.
        """
        pass


    def l(self):
        # Missing docstring.
        pass


    def m(self):
        """
        """
        # Empty docstring.
        pass



def moduleLevelFunctionWithoutDocstring():
    pass



from zope.interface import implementer, Interface



class IFoo(Interface):
    # An example of a locally defined interface
    # The interface should be documented
    def bar():
        # A locally defined interface method which should be
        # documented too.
        pass


@implementer(IFoo)
class FooImplementation(object):
    # The class which implements the interface must be documented.
    def bar(self):
        # This method implements part of the interface so doesn't
        # require documentation.
        pass


    def baz(self):
        # This method is not part of the interface so should be
        # documented.
        pass



import twistedchecker.functionaltests.example_interfaces
from twistedchecker import functionaltests
from twistedchecker.functionaltests.example_interfaces import IFoo2



@implementer(twistedchecker.functionaltests.example_interfaces.IFoo)
class FooImplementationExternalAbsoluteInterface(object):
    # A class whose interface is referenced using a fully qualified
    # module name.
    def bar(self):
        pass



@implementer(functionaltests.example_interfaces.IFoo2)
class FooImplementationExternalRelativeModuleInterface(object):
    # A class whose interface is referenced using a relative qualified
    # module name.
    def bar(self):
        pass



@implementer(functionaltests.example_interfaces.IFoo, IFoo2)
class FooImplementationExternalMultipleInterface(object):
    # A class which implements multiple interfaces
    def bar(self):
        pass
