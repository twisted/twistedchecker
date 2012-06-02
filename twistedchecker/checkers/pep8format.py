import sys

from logilab import astng
from logilab.common.ureports import Table
from logilab.astng import are_exclusive

from pylint.interfaces import IRawChecker, IASTNGChecker
from pylint.checkers import BaseRawChecker
from pylint.checkers.utils import check_messages
from pylint.checkers.format import FormatChecker

import pep8

class PEP8Checker(FormatChecker):
    """
    A checker for checking pep8 issues.
    Need pep8 installed.
    """
    msgs = {
     'W0291': ('Trailing whitespace found in the end of line',
               'Used when a line contains a trailing space.'),
     'W0293': ('Blank line contains whitespace',
               'Used when found a line contains whitespace.'),
     # messages for checking blank lines
     'E0301': ('expected 2 blank lines, found %d',
               ''),
     'E0302': ('expected 3 blank lines, found %d',
               ''),
     'E0303': ('too many blank lines, expected (%d)',
               ''),
     'E0304': ('blank lines found after function decorator',
               ''),
     'E0305': ('too many blank lines after docstring (%d)',
               ''),
    }
    __implements__ = (IRawChecker, IASTNGChecker)
    name = 'pep8'
    options = ()


    def __init__(self, linter=None):
        """
        Mannualy set max_module_lines to avoid errors.

        @param linter: C{PyLinter} object.
        """
        BaseRawChecker.__init__(self, linter)
        self.config.max_module_lines = 1000


    def new_line(self, tok_type, line, linenum, junk):
        """
        a new line has been encountered.

        @param tok_type: token type
        @param line: line
        @param linenum: line number
        @param junk: junk tokens
        """
        self._checkTrailingSpace(line, linenum)


    def _checkTrailingSpace(self, line, linenum):
        """
        Check line contains a trailing space.

        @param line: line to check
        @param linenum: line number
        """
        result = pep8.trailing_whitespace(line)
        if result:
            column, msg = result
            msgid = msg.split(" ")[0].replace("W", "W0")
            self.add_message(msgid, line=linenum)


    def blank_lines(logical_line, blank_lines, indent_level, line_number,
                previous_logical, previous_indent_level,
                blank_lines_before_comment):
        """
        This function is copied from a modified pep8 checker fot Twisted.
        See https://github.com/cyli/TwistySublime/blob/master/twisted_pep8.py
        Twisted Coding Standard:

        Separate top-level function and class definitions with three blank lines.
        Method definitions inside a class are separated by two blank lines.

        Extra blank lines may be used (sparingly) to separate groups of related
        functions.  Blank lines may be omitted between a bunch of related
        one-liners (e.g. a set of dummy implementations).

        Use blank lines in functions, sparingly, to indicate logical sections.

        Okay: def a():\n    pass\n\n\n\ndef b():\n    pass
        Okay: class A():\n    pass\n\n\n\nclass B():\n    pass
        Okay: def a():\n    pass\n\n\n# Foo\n# Bar\n\ndef b():\n    pass

        E301: class Foo:\n    b = 0\n    def bar():\n        pass
        E302: def a():\n    pass\n\ndef b(n):\n    pass
        E303: def a():\n    pass\n\n\n\ndef b(n):\n    pass
        E303: def a():\n\n\n\n    pass
        E304: @decorator\n\ndef a():\n    pass
        E305: "comment"\n\n\ndef a():\n    pass
        E306: variable="value"\ndef a():   pass
        """

        def isClassDefDecorator(thing):
            return (thing.startswith('def ') or
                    thing.startswith('class ') or
                    thing.startswith('@'))

        # Don't expect blank lines before the first line
        if line_number == 1:
            return

        max_blank_lines = max(blank_lines, blank_lines_before_comment)
        previous_is_comment = DOCSTRING_REGEX.match(previous_logical)

        # no blank lines after a decorator
        if previous_logical.startswith('@'):
            if max_blank_lines:
                return 0, "E304 blank lines found after function decorator"

        # should not have more than 3 blank lines
        elif max_blank_lines > 3 or (indent_level and max_blank_lines > 2):
            return 0, "E303 too many blank lines (%d)" % max_blank_lines

        elif isClassDefDecorator(logical_line):
            if indent_level:
                # There should only be 1 line or less between docstrings and
                # the next function
                if previous_is_comment:
                    if max_blank_lines > 1:
                        return 0, (
                            "E305 too many blank lines after docstring (%d)" %
                            max_blank_lines)

                # between first level functions, there should be 2 blank lines.
                # any further indended functions can have one or zero lines
                else:
                    if not (max_blank_lines == 2 or
                            indent_level > 4 or
                            previous_indent_level <= indent_level):
                        return 0, ("E301 expected 2 blank lines, found %d" %
                                       max_blank_lines)

            # top level, there should be 3 blank lines between class/function
            # definitions (but not necessarily after varable declarations)
            elif previous_indent_level and max_blank_lines != 3:
                return 0, "E302 expected 3 blank lines, found %d" % max_blank_lines

        elif max_blank_lines > 1 and indent_level:
            return 0, "E303 too many blank lines, expected (%d)" % max_blank_lines
