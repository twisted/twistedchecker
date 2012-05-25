import sys
import StringIO

from twisted.trial import unittest

import twistedchecker
from twistedchecker.core.runner import Runner


class FormatTestCase(unittest.TestCase):
    """
    Test for checking format issues.
    """

    def setUp(self):
        """
        Redirect stdout to a temp C{StringIO} stream.
        """
        self.outputStream = StringIO.StringIO()
        self.patch(sys, "stdout", self.outputStream)


    def test_indent(self):
        """
        Test for checking indent, Twisted uses 4 spaces.
        """
        runner = Runner()
        runner.setOutput(self.outputStream)
        testmodule = "twistedchecker.testsuit.indentation"
        runner.run([testmodule])
        messagesShouldAppear = \
            ["W:  7,0: Bad indentation. Found 2 spaces, expected 4",
             "W: 11,0: Found indentation with tabs instead of spaces"]
        for message in messagesShouldAppear:
            self.assertTrue(self.outputStream.getvalue().count(message) > 0)
