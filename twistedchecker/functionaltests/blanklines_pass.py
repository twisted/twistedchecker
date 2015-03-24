# enable: W9012,W9013,W9015,W9016

# Top-level classes should be separated with 3 blank lines
class a:
    # class level functions with 2 blank lines
    def a(self):
        pass


    def methodWithDocstringWithoutBody(self):
        """
        A valid method without a body.
        """


    def b(self):
        pass



class b:
    pass



# Top-level functions should be separated with 3 blank lines
def c():
    pass



def d():
    pass



def foo():
    """
    There should be one blank line or less between
    a docstring and a function definition.
    """
    def bar():
        pass
    # No more than one blank line between two statements.

    a = 1
