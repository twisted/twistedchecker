# enable: W9603

def foo(x, y):
    """
    A function.
    """
    pass

# The built-in function apply is deprecated.

apply(foo, (1, 2))


def bar():
    apply(foo, 1, 2) # this should cause warning

bar()
