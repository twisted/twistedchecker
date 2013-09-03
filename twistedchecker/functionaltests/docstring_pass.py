# enable: W9201,W9202,W9203,W9204,W9205,W9206,W9207,W9208,W9209
"""
A docstring with a wrong indentation.
Docstring should have consistent indentations.
"""

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


    def f(self):
        """
        A method returns nothing.
        """
        return



from zope.interface import implementer, Interface



class IFoo(Interface):
    """
    An example of a locally defined interface
    The interface should be documented
    """
    def bar():
        """
        A locally defined interface method which should be
        documented too.
        """
        pass



@implementer(IFoo)
class FooImplementation(object):
    """
    The class which implements the interface must be documented.
    """
    def bar(self):
        # This method implements part of the interface so doesn't
        # require documentation.
        pass


    def baz(self):
        """
        This method is not part of the interface so should be
        documented.
        """
        pass



import twistedchecker.functionaltests._example_interfaces
from twistedchecker import functionaltests
from twistedchecker.functionaltests._example_interfaces import IFoo2



@implementer(twistedchecker.functionaltests._example_interfaces.IFoo)
class FooImplementationExternalAbsoluteInterface(object):
    """
    A class whose interface is referenced using a fully qualified
    module name.
    """
    def bar(self):
        pass



@implementer(functionaltests._example_interfaces.IFoo2)
class FooImplementationExternalRelativeModuleInterface(object):
    """
    A class whose interface is referenced using a relative qualified
    module name.
    """
    def bar(self):
        pass



@implementer(functionaltests._example_interfaces.IFoo, IFoo2)
class FooImplementationExternalMultipleInterface(object):
    """
    A class which implements multiple interfaces
    """
    def bar(self):
        pass


@implementer(IFoo)
class FooImplementationConditionalMethods1(object):
    """
    A class whose methods are not direct children in the node tree.
    """
    try:
        def bar(self):
            # An interface implementation method still inherits the
            # interface documentation if it's within another scoped
            # node such as try...except
            pass
    except:
        pass
