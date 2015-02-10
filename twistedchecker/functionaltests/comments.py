# enable: W9401,W9402

#A comment does not begin with a whitespace.

a = 1 + 2  #  A coment begins with two whitespace.

# a comment begins with a lowercase letter.

# Good comment examples.

# A sentence that spans multiple lines
# doesn't need to have capitalization on second line.

# Here's some code samples:
#  x = x + 1

# Make sure no error occur when checking an empty comment
#

"""
#twisted checker things this is a comment and so
1. Comments should begin with one whitespace
2. The first letter of comment should be capitalized

This is particularly triggered with url fragments
@see U{https://example.com/test#fragment}
"""


class SomeClass(object):
    """
    #twisted checker things this is a comment.

    Also triggered with url fragments U{https://example.com/test#fragment}
    """
