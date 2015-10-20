# enable: C0103

# Bad examples

foo_bar = None

foo_barBaz = None

foo_Bar = None

# Good examples

FOO = None

FOO_BAR = None

Foo = None

FooBar = None

__FOO__ = None

foo = None

fooBar = None

_fooBar = None


class SomeClass(object):

    SOME_CONSTANT = 'some_value'

    def __init__(self):
        self.variable = self.SOME_CONSTANT
        # Constants can also act as instance variables,
        # for example, late initialization.
        self.SOME_CONSTANT = 'new-value'

    def otherMethod(me):
        me.variable = self.SOME_CONSTANT
        # Constants can also act as instance variables,
        # for example, late initialization.
        me.SOME_CONSTANT = 'new-value'

    @classmethod
    def someMethod(cls):
        cls.variable = cls.SOME_CONSTANT
        # Constants can also act as class variables,
        # for example, late initialization.
        cls.SOME_CONSTANT = 'new-value'
