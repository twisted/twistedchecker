# enable: W9401,W9402

#A comment does not begin with a whitespace.

someVariable = 1 + 2  #  A comment begins with two whitespace.

# a comment begins with a lowercase letter.

# Good comment examples.

# A sentence that spans multiple lines
# doesn't need to have capitalization on second line.

# Here's some code samples:
#  x = x + 1

# Make sure no error occur when checking an empty comment
#

"""
#twisted checker thinks this is a comment and so
1. Comments should begin with one whitespace
2. The first letter of comment should be capitalized

Line with an epydoc C{#} markup.

This is particularly triggered with url fragments
@see U{https://example.com/test#fragment}
"""

#This comment should be reported.

someVariable = 1 + 2 #  So does this one.

class SomeClass(object):
    """
    #twisted checker thinks this is a comment.

    Line with an epydoc C{#} markup.

    Also triggered with url fragments U{https://example.com/test#fragment}
    """
    #But this comment should be reported.

# '\r\n\t' a comment can start with a new lines characters.

var = 1 + 2  # \r\n same for inline comments.

# `literal` is fine at the start.

