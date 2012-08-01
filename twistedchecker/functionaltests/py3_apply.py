# enable: W9603

def foo(x, y):
    """
    A function.
    """
    pass

# The built-in function apply is deprecated.

apply(foo, (1, 2))

# Call apply method on a object

class Bar:
    """
    A class.
    """

    def apply(self, x, y):
        """
        A method named "apply".
        """
        pass


baz = Bar()

# No warning should be generated
baz.apply(1, 2)

# Should not warn if the apply function is imported from somewhere else

from os.path import exists as apply

apply("foo")
