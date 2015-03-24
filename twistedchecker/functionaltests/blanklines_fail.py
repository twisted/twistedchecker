# enable: W9012,W9013,W9015,W9016

# Top-level classes separated with 2 blank lines,
# should be 3
class a:
    # class level functions with 1 blank lines
    # should be 2
    def a(self):
        pass

    def b(self):
        pass


class b:
    pass



# Top-level functions separated with 4 blank lines
# should be 3
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
        """
        This is defined to far from previous block.
        """
    # Too many blank lines after this line.


    a = 1
