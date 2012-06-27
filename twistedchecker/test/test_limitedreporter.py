import sys
import os
import StringIO

from twisted.trial import unittest

import twistedchecker
from twistedchecker.core.runner import Runner
from twistedchecker.reporters.limited import LimitedReporter


class LimitedReporterTestCase(unittest.TestCase):
    """
    Test for twistedchecker.reporter.limited.LimitedReporter.
    """

    def test_loadAllowedMessages(self):
        """
        Test for _loadAllowedMessages method.
        Make sure some messages are loaded
        and all of them should begin be tokens in 5 letters.
        """
        reporter = LimitedReporter()
        reporter._loadAllowedMessages()
        # assert some messages are loaded
        self.assertTrue(reporter.messagesAllowed)
        # assert they are 5 letter tokens
        for msgid in reporter.messagesAllowed:
            self.assertEqual(len(msgid), 5)


    def test_reporter(self):
        """
        Test for LimitedReporter.
        Use test file of indentation to test
        whether limited messages are returned when using LimitedReporter.
        Defaultly test on this test file will return two warnings:
        W0311 and W0312.
        """
        moduleTestIndentation = "twistedchecker.functionaltests.indentation"
        pathTestIndentation = os.path.join(twistedchecker.abspath,
                                      "functionaltests", "indentation.py")
        # assert the test file exists
        self.assertTrue(os.path.exists(pathTestIndentation))
        streamTestResult = StringIO.StringIO()
        runner = Runner()
        runner.setOutput(streamTestResult)
        # defaultly, runner will use LimitedReporter as its output reporter
        # set allowed messages for it
        runner.linter.reporter.messagesAllowed = set(["W0311"])
        runner.run([moduleTestIndentation])
        # check the results to see only W0311 is reported
        resultTest = streamTestResult.getvalue()
        self.assertTrue("W0311" in resultTest)
        self.assertTrue("W0312" not in resultTest)
