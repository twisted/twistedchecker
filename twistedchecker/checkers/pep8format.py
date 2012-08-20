import sys
import StringIO
import re
import inspect

from logilab import astng
from logilab.common.ureports import Table
from logilab.astng import are_exclusive

from pylint.interfaces import IASTNGChecker
from pylint.reporters import diff_string
from pylint.checkers import BaseChecker, EmptyReport

import pep8
from pep8 import DOCSTRING_REGEX
from pep8 import Checker as PEP8OriginalChecker

class PEP8WarningRecorder(PEP8OriginalChecker):
    """
    A subclass of pep8's checker that records warnings.
    """

    def __init__(self, file):
        """
        Initate warnings.

        @param file: file to be checked
        """
        pep8.options = pep8.process_options([file])[0]
        PEP8OriginalChecker.__init__(self, file)
        self.report_error = self.errorRecorder
        self.warnings = []
        self.run()


    def errorRecorder(self, lineNumber, offset, text, check):
        """
        A function to override report_error in pep8.
        And record output warnings.

        @param lineNumber: line number
        @param offset: column offset
        @param text: warning message
        @param check: check object in pep8
        """
        code = text.split(" ")[0]
        if hasattr(self, 'report'):
            lineOffset = self.report.line_offset
        else:
            # old pep8.py
            lineOffset = self.line_offset

        self.warnings.append((lineOffset + lineNumber,
                              offset + 1, code, text))


    def run(self):
        """
        Run pep8 checker and record warnings.
        """
        # set a stream to replace stdout, and get results in it
        stdoutBak = sys.stdout
        streamResult = StringIO.StringIO()
        sys.stdout = streamResult
        try:
            PEP8OriginalChecker.check_all(self)
        finally:
            sys.stdout = stdoutBak



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
     'W9012': ('Expected 2 blank lines, found %s',
               'Class-level functions should be separated '
               'with 2 blank lines.'),
     'W9013': ('Expected 3 blank lines, found %s',
               'Top-level functions should be separated '
               'with 3 blank lines.'),
     'W9015': ('Too many blank lines, expected %s',
               'Used when too many blank lines are found.'),
     'W9016': ('Too many blank lines after docstring, found %s',
               'Used when too many blank lines after docstring are found.'),
     # general pep8 warnings
     'W9017': ('Blank line at end of file',
               'More than one blank line found at end of file (W391 in pep8).'),
     'W9018': ('No newline at end of file',
               'No blank line is found at end of file (W292 in pep8).'),
     'W9019': ("Whitespace after '%s'",
               'Redundant whitespace found after a symbol (E201 in pep8).'),
     'W9020': ("Whitespace before '%s'",
               'Redundant whitespace found before a symbol (E202 in pep8).'),
     'W9021': ("Missing whitespace after '%s'",
               "Expect a whitespace after a symbol (E231 in pep8)."),
     'W9022': ("Multiple spaces after operator",
               "Found multiple spaces after an operator (E222 in pep8)."),
     'W9023': ("Multiple spaces before operator",
               "Found multiple spaces before an operator (E221 in pep8)."),
     'W9024': ("Missing whitespace around operator",
               "No space found around an operator (E225 in pep8)."),
     'W9025': ("No spaces should be around keyword / parameter equals",
               "Spaces found around keyword or parameter equals "
               "(E251 in pep8)."),
     'W9026': ("At least two spaces before inline comment",
               "Found less than two spaces before inline comment "
               "(E261 in pep8)."),
    }
    standardPEP8Messages = ['W%d' % id for id in range(9017,9027)]
    pep8Enabled = None
    __implements__ = IASTNGChecker
    name = 'pep8'
    # map pep8 messages to messages in pylint.
    # it's foramt should look like this:
    # 'msgid in pep8' : ('msgid in pylint','a string to extract arguments')
    mapPEP8Messages = {
        'W291': ('W9010', ''),
        'W293': ('W9011', ''),
        'E301': ('W9012', r'expected 2 blank lines, found (\d+)'),
        'E302': ('W9013', r'expected 3 blank lines, found (\d+)'),
        'E303': ('W9015', r'too many blank lines, expected \((\d+)\)'),
        'E305': ('W9016', r'too many blank lines after docstring \((\d+)\)'),
        'W391': ('W9017', ''),
        'W292': ('W9018', ''),
        'E201': ('W9019', r"whitespace after '%s'"),
        'E202': ('W9020', r"whitespace before '%s'"),
        'E203': ('W9020', r"whitespace before '%s'"),
        'E211': ('W9020', r"whitespace before '%s'"),
        'E231': ('W9021', r"missing whitespace after '%s'"),
        'E222': ('W9022', ''),
        'E221': ('W9023', ''),
        'E225': ('W9024', ''),
        'E251': ('W9025', ''),
        'E261': ('W9026', ''),
    }
    warnings = None
    pep8Checker = None

    def __init__(self, linter):
        """
        Change function of processing blank lines in pep8.

        @param linter: current C{PyLinter} object.
        """
        BaseChecker.__init__(self, linter)
        argumentsBlankLines = inspect.getargspec(pep8.blank_lines).args
        if 'blank_lines_before_comment' in argumentsBlankLines:
            # using old pep8.py
            pep8.blank_lines = modifiedBlankLinesForOldPEP8
        else:
            pep8.blank_lines = modifiedBlankLines
        self.pep8Enabled = self.linter.option_value("pep8")


    def visit_module(self, node):
        """
        A interface will be called when visiting a module.
        """
        self._runPEP8Checker(node.file)


    def _runPEP8Checker(self, file):
        """
        Call the checker of pep8

        @param file: path of module to check
        """
        recorder = PEP8WarningRecorder(file)
        self._outputMessages(recorder.warnings)


    def _outputMessages(self, warnings):
        """
        Map pep8 results to messages in pylint, then output them.

        @param warnings: it should be a list of tuple including
        line number and message id
        """
        if not warnings:
            # no warnings were found
            return
        for warning in warnings:
            linenum, offset, msgidInPEP8, text = warning
            if msgidInPEP8 in self.mapPEP8Messages:
                msgid, patternArguments = self.mapPEP8Messages[msgidInPEP8]
                if (not self.pep8Enabled and
                    msgid in self.standardPEP8Messages):
                    continue

                arguments = []
                if patternArguments:
                    matchResult = re.search(patternArguments, text)
                    if matchResult:
                        arguments = matchResult.groups()
                self.add_message(msgid, line=linenum, args=arguments)



def checkBlankLinesForPEP8(logical_line, blank_lines,
                                 indent_level, line_number,
                                 previous_logical, previous_indent_level,
                                 blank_lines_before_comment):
    """
    This function is copied from a modified pep8 checker for Twisted.
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

    # Check blank lines after a decorator,
    # but this checking is removed because no this requirement in
    # Twisted Coding Standard.
    # if previous_logical.startswith('@'):
    #     if max_blank_lines:
    #         return 0, "E304 blank lines found after function decorator"

    if isClassDefDecorator(logical_line):
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
            return (0,
                "E302 expected 3 blank lines, found %d" % max_blank_lines)

    elif max_blank_lines > 1 and indent_level:
        return 0, "E303 too many blank lines, expected (%d)" % max_blank_lines



def modifiedBlankLinesForOldPEP8(logical_line, blank_lines,
                                 indent_level, line_number,
                                 previous_logical, previous_indent_level,
                                 blank_lines_before_comment):
    """
    This function is same as modifiedBlankLines,
    but supports old version of pep8.py.
    """
    return checkBlankLinesForPEP8(logical_line, blank_lines,
                                 indent_level, line_number,
                                 previous_logical, previous_indent_level,
                                 blank_lines_before_comment)



def modifiedBlankLines(logical_line, blank_lines, indent_level, line_number,
                       previous_logical, previous_indent_level):
    """
    A function for checking blank lines as a replacement for that in pep8.py.

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
    result = checkBlankLinesForPEP8(logical_line, blank_lines,
                                 indent_level, line_number,
                                 previous_logical, previous_indent_level,
                                 0)
    if result:
        yield result
    else:
        return
