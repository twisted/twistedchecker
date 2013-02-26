# A module where all the docstrings are missing

from zope.interface import implementer



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
