import sys
import StringIO
import re

from logilab import astng
from logilab.common.ureports import Table
from logilab.astng import are_exclusive

from pylint.interfaces import IASTNGChecker
from pylint.reporters import diff_string
from pylint.checkers import BaseChecker, EmptyReport

import pep8
from pep8 import Checker as PEP8OriginalChecker

class PEP8WarningRecorder(PEP8OriginalChecker):
    """
    A subclass of pep8 checker and will record warnings.
    """
    warnings = None

    def __init__(self, file):
        """
        Initate warnings.

        @param file: file to be checked
        """
        pep8.options = pep8.process_options([file])[0]
        PEP8OriginalChecker.__init__(self, file)
        self.warnings = []
        self.run()


    def report_error(self, lineNumber, offset, text, check):
        """
        A function to override report_error in pep8.
        And record output warings.

        @param lineNumber: line number
        @param offset: column offset
        @param text: warning message
        @param check: check object in pep8
        """
        code = text[:4]
        self.warnings.append((self.line_offset + lineNumber,
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
               'Used when found a line contains whitespaces.')
    }
    __implements__ = IASTNGChecker
    name = 'pep8'
    # map pep8 messages to messages in pylint.
    # it's foramt should look like this:
    # 'msgid in pep8' : ('msgid in pylint','a string to extract arguments')
    mapPEP8Messages = {
        'W291': ('W9010', ''),
        'W293': ('W9011', ''),
    }
    warnings = None
    pep8Checker = None


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
                arguments = []
                if patternArguments:
                    matchResult = re.search(patternArguments, text)
                    if matchResult:
                        arguments = matchResult.groups()
                self.add_message(msgid, line=linenum, args=arguments)
