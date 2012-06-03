import sys
import StringIO

from logilab import astng
from logilab.common.ureports import Table
from logilab.astng import are_exclusive

from pylint.interfaces import IASTNGChecker
from pylint.reporters import diff_string
from pylint.checkers import BaseChecker, EmptyReport

import pep8

class PEP8Checker(BaseChecker):
    """
    A checker for checking pep8 issues.
    Need pep8 installed.
    """
    msgs = {
     'W9010': ('Trailing whitespace found in the end of line',
               'Used when a line contains a trailing space.'),
     'W9011': ('Blank line contains whitespace',
               'Used when found a line contains whitespace.'),
     # messages for checking blank lines
     'W9012': ('expected 2 blank lines, found %d',
               'There should 2 lines between methods'),
     'W9013': ('expected 3 blank lines, found %d',
               'ccqcqwe qwe qw  q'),
     'W9014': ('too many blank lines, expected (%d)',
               'qwe afqd qw qweqwe qweq we qw wqe qwewq'),
     'W9015': ('blank lines found after function decorator',
               'casad qwe qw sd'),
     'W9016': ('too many blank lines after docstring (%d)',
               'qwfqw qwe q qwqg'),
    }
    __implements__ = IASTNGChecker
    name = 'pep8'

    mapPEP8Messages = {
        'W291': 'W9010',
        'W293': 'W9011',
        'E301': 'W9012',
        'E302': 'W9013',
        'E303': 'W9014',
        'E304': 'W9015',
        'E305': 'W9016',
    }

    def __init__(self,linter):
        """
        Change function of processing blank lines in pep8.

        @param linter: current C{PyLinter} object.
        """
        pep8.blank_lines = self.blank_lines


    def visit_module(self, node):
        """
        A interface will be called when visiting a module.
        """
        self._runPEP8Checker(node.file)


    def _runPEP8Checker(self, file):
        """
        Call the checker of pep8
        """
        pep8.options = pep8.process_options([file])[0]
        checker = pep8.Checker(file)
        # backup stdout
        bakStdout = sys.stdout
        # set a stream to replace stdout, and get results in it
        streamResult = StringIO.StringIO()
        sys.stdout = streamResult
        checker.check_all()
        sys.stdout = bakStdout
        self._outputMessages(streamResult.getvalue())


    def _outputMessages(self, pep8result):
        """
        Map pep8 results to messages in pylint, then output them.

        @param pep8result: results of pep8
        """
        linesResult = [l for l in pep8result.split("\n") if l]
        for line in linesResult:
            msgidInPEP8 = line.split(" ")[1]
            if msgidInPEP8 in self.mapPEP8Messages:
                msgid = self.mapPEP8Messages[msgidInPEP8]
                linenum = line.split(":")[1]
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
