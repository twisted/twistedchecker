# enable: W9604

# A good example.
try:
    pass
except Exception as e:
    pass


# except exc, var is no longer supported in python 3.
try:
    pass
except Exception, e:
    pass

# make sure it works for try...except...finally

try:
    pass
except Exception, e:
    pass
finally:
    pass
