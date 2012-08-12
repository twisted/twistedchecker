# enable: W9603

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

# Alias of other functions
import os.path

apply = os.path.exists

apply("foo")

# Should not warn if the apply function is imported from somewhere else

from os.path import exists as apply

apply("foo")
