# enable: W9019,W9020,W9021,W9022,W9023,W9024,W9025,W9026,W9027

# Whitespace after '['.
a = [ 1, 2]

# Whitespace before ']'.
a = [1, 2 ]

# Missing whitespace after ','.
a = [1,2]

# Good example.
a = [1, 2]

# Multiple spaces found afer '='.
b =  1

# Multiple spaces found before '='.
b  = 1

# Missing whitespace around '='
b=1

# Good example.
b = 1

# Spaces found around parameter equal.
[].sort(revert = True)

# Good example.
[].sort(revert=True)

# Only one space before inline comment.
c = 1 # an inline comment

# Good example.
c = 1  # an inline comment

# Example of a well-done decorator
@imaginarydecorator
def correct_decorator():
	pass

# Example of a decorator with incorrect spacing
@imaginarydecorator

def incorrect_decorator():
	pass
