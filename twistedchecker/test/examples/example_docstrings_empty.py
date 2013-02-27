# A module where all the docstrings are missing

"""

"""

from zope.interface import implementer, Interface


def bar():
    """

    """
    pass



class Foo(object):
    """

    """
    def bar(self):
        """

        """
        pass



class IFoo(Interface):
    """

    """
    def bar():
        """

        """
        pass



@implementer(IFoo)
class FooImplementation(object):
    """

    """
    def bar(self):
        """

        """
        pass
