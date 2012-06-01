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
               'Used when found a line contains whitespace.')
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
