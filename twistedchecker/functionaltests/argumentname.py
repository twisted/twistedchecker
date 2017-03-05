# enable: C0103

# Argument names are same as variable names

# Bad examples
# Pylint will generate two warnings for each bad argument name,
# one for invalid argument name, and one for invalid variable name.

def functiona(FooBar):
    pass

def functionb(Foo):
    pass

def functionc(FOO):
    pass

def functiond(foo_bar):
    pass

# Good examples
def functione(f):
    pass

def functionf(foo):
    pass

def functiong(_foo):
    pass

def functionh(fooBar):
    pass
