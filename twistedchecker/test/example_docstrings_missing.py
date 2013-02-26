# A module where all the docstrings are missing

from zope.interface import implementer

import example_interfaces



def bar():
    pass



class Foo(object):
    def bar(self):
        pass



class IFoo(object):
    def bar():
        pass



@implementer(IFoo)
class FooImplementation(object):
    def bar(self):
        pass



@implementer(example_interfaces.IFoo)
class FooImplementationExternal(object):
    def bar(self):
        pass
