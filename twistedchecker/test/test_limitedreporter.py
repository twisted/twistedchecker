import os

from io import StringIO

from twisted.trial import unittest

import twistedchecker
from twistedchecker.core.runner import Runner



class LimitedReporterTestCase(unittest.TestCase):
    """
    Test for twistedchecker.reporter.limited.LimitedReporter.
    """

    def test_reporter(self):
        """
        Test for LimitedReporter.
        Use test file of indentation to test
        whether limited messages are returned when using LimitedReporter.

        Complete run on the test file will return two warnings:
        W0311 and W0312, but with limited report it returns only one.
        """
        moduleTestIndentation = "twistedchecker.functionaltests.indentation"
        pathTestIndentation = os.path.join(twistedchecker.abspath,
                                      "functionaltests", "indentation.py")
        # assert the test file exists
        self.assertTrue(os.path.exists(pathTestIndentation))
        streamTestResult = StringIO()
        runner = Runner()
        runner.setOutput(streamTestResult)
        # defaultly, runner will use LimitedReporter as its output reporter
        # set allowed messages for it
        runner.linter.reporter.messagesAllowed = set(["W0311"])

        exitResult = self.assertRaises(
            SystemExit, runner.run, [moduleTestIndentation])

        # check the results to see only W0311 is reported
        resultTest = streamTestResult.getvalue()
        self.assertTrue("W0311" in resultTest)
        self.assertTrue("W0312" not in resultTest)
        self.assertEqual(4, exitResult.code)
