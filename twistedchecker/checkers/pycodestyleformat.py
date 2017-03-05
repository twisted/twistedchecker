# -*- test-case-name: twistedchecker.test.test_runner -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Checks the code using pycodestyle.py and a custom blank line checker that
matches the Twisted Coding Standard.
"""

import sys
import re

from io import StringIO

from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker

import pycodestyle



class PyCodeStyleWarningRecorder(pycodestyle.Checker):
    """
    A subclass of pycodestyle's checker that records warnings.
    """

    def __init__(self, file):
        """
        Initate warnings.

        @param file: file to be checked
        """
        pycodestyle.Checker.__init__(self, file)

        for item in self._logical_checks:
            # This cycles through all of the logical checks that the Checker
            # does. The reason why we have to monkeypatch it here is that
            # upon init, it makes a list of all of the plugins/functions it
            # has, and therefore already /has/ a reference to the
            # blank_lines that we don't want. So this cycles over the logical
            # checks, and replaces the old blank_lines with the one that
            # matches Twisted's blank spaces convention.
            if item[0] == "blank_lines":
                replacetuple = (item[0], modifiedBlankLines, item[2])
                self._logical_checks[
                    self._logical_checks.index(item)] = replacetuple

        self.report_error = self.errorRecorder
        self.warnings = []
        self.run()


    def errorRecorder(self, lineNumber, offset, text, check):
        """
        A function to override report_error in pycodestyle.
        And record output warnings.

        @param lineNumber: line number
        @param offset: column offset
        @param text: warning message
        @param check: check object in pycodestyle
        """
        code = text.split(" ")[0]
        lineOffset = self.report.line_offset

        self.warnings.append((lineOffset + lineNumber,
                              offset + 1, code, text))


    def run(self):
        """
        Run pycodestyle checker and record warnings.
        """
        # Set a stream to replace stdout, and get results in it
        stdoutBak = sys.stdout
        streamResult = StringIO()
        sys.stdout = streamResult
        try:
            pycodestyle.Checker.check_all(self)
        finally:
            sys.stdout = stdoutBak


_counter = iter(range(100))


class PyCodeStyleChecker(BaseChecker):
    """
    A checker for checking pycodestyle issues.
    Need pycodestyle installed.
    """
    msgs = {
        'W9010': ('Trailing whitespace found in the end of line',
                  'Used when a line contains a trailing space.', "pycodestyle" + str(next(_counter))),
        'W9011': ('Blank line contains whitespace',
                  'Used when found a line contains whitespace.', "pycodestyle" + str(next(_counter))),
        # Messages for checking blank lines
        'W9012': ('Expected 2 blank lines, found %s',
                  'Class-level functions should be separated '
                  'with 2 blank lines.', "pycodestyle" + str(next(_counter))),
        'W9013': ('Expected 3 blank lines, found %s',
                  'Top-level functions should be separated '
                  'with 3 blank lines.', "pycodestyle" + str(next(_counter))),
        'W9015': ('Too many blank lines, found %s',
                  'Used when too many blank lines are found.', "pycodestyle" + str(next(_counter))),
        'W9016': ('Too many blank lines after docstring, found %s',
                  'Used when too many blank lines after docstring are found.', "pycodestyle" + str(next(_counter))),
        'W9027': ("Blank lines found after a function decorator",
                  "Function decorators should be followed with blank lines.", "pycodestyle" + str(next(_counter))),
        # General pycodestyle warnings
        'W9017': ('Blank line at end of file',
                  'More than one blank line found at EOF (W391 in pycodestyle).', "pycodestyle" + str(next(_counter))),
        'W9018': ('No newline at end of file',
                  'No blank line is found at end of file (W292 in pycodestyle).', "pycodestyle" + str(next(_counter))),
        'W9019': ("Whitespace after '%s'",
                  'Redundant whitespace found after a symbol (E201 in pycodestyle).', "pycodestyle" + str(next(_counter))),
        'W9020': ("Whitespace before '%s'",
                  'Redundant whitespace found before a symbol '
                  '(E202 in pycodestyle).', "pycodestyle" + str(next(_counter))),
        'W9021': ("Missing whitespace after '%s'",
                  "Expect a whitespace after a symbol (E231 in pycodestyle).", "pycodestyle" + str(next(_counter))),
        'W9022': ("Multiple spaces after operator",
                  "Found multiple spaces after an operator (E222 in pycodestyle).", "pycodestyle" + str(next(_counter))),
        'W9023': ("Multiple spaces before operator",
                  "Found multiple spaces before an operator (E221 in pycodestyle).", "pycodestyle" + str(next(_counter))),
        'W9024': ("Missing whitespace around operator",
                  "No space found around an operator (E225 in pycodestyle).", "pycodestyle" + str(next(_counter))),
        'W9025': ("No spaces should be around keyword / parameter equals",
                  "Spaces found around keyword or parameter equals "
                  "(E251 in pycodestyle).", "pycodestyle" + str(next(_counter))),
        'W9026': ("At least two spaces before inline comment",
                  "Found less than two spaces before inline comment "
                  "(E261 in pycodestyle).", "pycodestyle" + str(next(_counter))),
    }
    standardPyCodeStyleMessages = ['W%d' % (id,) for id in range(9017,9027)]
    pycodestyleEnabled = None
    __implements__ = IAstroidChecker
    name = 'pycodestyle'
    # Map pycodestyle messages to messages in pylint.
    # The format should look like this:
    # 'msgid in pycodestyle' : ('msgid in pylint','a string to extract arguments')
    mapPyCodeStyleMessages = {
        'W291': ('W9010', ''),
        'W293': ('W9011', ''),
        'E301': ('W9012', r'expected 2 blank lines, found (\d+)'),
        'E302': ('W9013', r'expected 3 blank lines, found (\d+)'),
        'E303': ('W9015', r'too many blank lines \((\d+)\)'),
        'E304': ('W9027', ''),
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
    pycodestyleChecker = None

    def __init__(self, linter):
        """
        Change function of processing blank lines in pycodestyle.

        @param linter: current C{PyLinter} object.
        """
        BaseChecker.__init__(self, linter)
        self.pycodestyleEnabled = True # yes of course


    def visit_module(self, node):
        """
        A interface will be called when visiting a module.

        @param node: The module node to check.
        """
        recorder = PyCodeStyleWarningRecorder(node.file)
        self._outputMessages(recorder.warnings, node)


    def _outputMessages(self, warnings, node):
        """
        Map pycodestyle results to messages in pylint, then output them.

        @param warnings: it should be a list of tuple including
        line number and message id
        """
        if not warnings:
            # No warnings were found
            return
        for warning in warnings:
            linenum, offset, msgidInPyCodeStyle, text = warning

            if text.startswith(msgidInPyCodeStyle):
                # If the PyCodeStyle code is at the start of the text, trim it out
                text = text[len(msgidInPyCodeStyle) + 1:]

            if msgidInPyCodeStyle in self.mapPyCodeStyleMessages:
                msgid, patternArguments = self.mapPyCodeStyleMessages[msgidInPyCodeStyle]
                if (not self.pycodestyleEnabled and
                    msgid in self.standardPyCodeStyleMessages):
                    continue

                arguments = []
                if patternArguments:
                    matchResult = re.search(patternArguments, text)
                    if matchResult:
                        arguments = matchResult.groups()
                self.add_message(msgid, line=linenum, args=arguments, node=node)



def modifiedBlankLines(logical_line, blank_lines, indent_level, line_number,
                       blank_before, previous_logical, previous_indent_level):
    """
    This function is copied from a modified pycodestyle checker for Twisted.
    See https://github.com/cyli/TwistySublime/blob/master/twisted_pycodestyle.py
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

    @param logical_line: Supplied by PyCodeStyle. The content of the line it is dealing with.
    @param blank_lines: Supplied by PyCodeStyle.
    @param indent_level: Supplied by PyCodeStyle. The current indent level.
    @param line_number: Supplied by PyCodeStyle. The current line number.
    @param blank_before: Supplied by PyCodeStyle. The number of blank lines before this one.
    @param previous_logical: Supplied by PyCodeStyle. The previous logical line.
    @param previous_indent_level: Supplied by PyCodeStyle. The indent level of the previous line.
    """
    def isClassDefDecorator(thing):
        return (thing.startswith('def ') or
                thing.startswith('class ') or
                thing.startswith('@'))

    # Don't expect blank lines before the first line
    if line_number == 1:
        return

    previous_is_comment = pycodestyle.DOCSTRING_REGEX.match(previous_logical)

    # Check blank lines after a decorator,
    if previous_logical.startswith('@'):
        if blank_before:
            yield 0, "E304 blank lines found after function decorator"

    if isClassDefDecorator(logical_line):
        if indent_level:
            # There should only be 1 line or less between docstrings and
            # the next function
            if previous_is_comment:
                # Previous is a comment so it has one extra indentation.
                at_same_indent = previous_indent_level - 4 == indent_level
                if (
                    at_same_indent and
                    logical_line.startswith('def ') and
                    blank_before == 2
                        ):
                    # This look like a previous method with a docstring
                    # and empty body.
                    return
                if blank_before > 1:
                    yield 0, (
                        "E305 too many blank lines after docstring "
                        "(%d)" % (blank_before,))

            # Between first level functions, there should be 2 blank lines.
            # any further indended functions can have one or zero lines
            else:
                if not (blank_before == 2 or
                        indent_level > 4 or
                        previous_indent_level <= indent_level):
                    yield 0, ("E301 expected 2 blank lines, "
                              "found %d" % (blank_before,))

        # Top level, there should be 3 blank lines between class/function
        # definitions (but not necessarily after variable declarations)
        elif previous_indent_level and blank_before != 3:
            yield 0, ("E302 expected 3 blank lines, "
                      "found %d" % (blank_before,))

    elif blank_before > 1 and indent_level:
        yield 0, "E303 too many blank lines (%d)" % (blank_before,)
