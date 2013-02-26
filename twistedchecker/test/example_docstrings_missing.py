# A module where all the docstrings are missing

from zope.interface import implementer, Interface

import example_interfaces
from example_interfaces.foo import IFoo2



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



@implementer(example_interfaces.foo.IFoo)
class FooImplementationExternal(object):
    def bar(self):
        pass



@implementer(IFoo2)
class FooImplementationExternal2(object):
    def bar(self):
        pass



@implementer(example_interfaces.foo.IFoo, IFoo2)
class FooImplementationExternal3(object):
    def bar(self):
        pass
