# A module where all the docstrings are missing

from zope.interface import implementer, Interface

import examples.example_interfaces
from examples.example_interfaces import IFoo2



def bar():
    pass



class Foo(object):
    def bar(self):
        pass



class IFoo(Interface):
    def bar():
        pass



@implementer(IFoo)
class FooImplementation(object):
    def bar(self):
        pass



@implementer(examples.example_interfaces.IFoo)
class FooImplementationExternalAbsoluteInterface(object):
    def bar(self):
        pass



@implementer(IFoo2)
class FooImplementationExternalRelativeInterface(object):
    def bar(self):
        pass



@implementer(examples.example_interfaces.IFoo, IFoo2)
class FooImplementationExternalMultipleInterface(object):
    def bar(self):
        pass
