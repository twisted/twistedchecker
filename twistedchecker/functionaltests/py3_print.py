# enable: W9601
import sys
# Bad examples did not use parens

print (1, 2)

print "The answer is", 2 * 2

print 2,

print

print >>sys.stderr, "fatal error"

# Good examples corresponding to good examples
# two lines of code are commented, because they will cause error in python 2.x

print((1, 2))

print("The answer is", 2 * 2)

#print(2, end=" ")

print()

#print("fatal error", file=sys.stderr)
