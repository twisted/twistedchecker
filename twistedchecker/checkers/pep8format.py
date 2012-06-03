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
               'Used when found a line contains whitespace.')
    }
    __implements__ = IASTNGChecker
    name = 'pep8'

    mapPEP8Messages = {
        'W291': 'W9010',
        'W293': 'W9011',
    }


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
