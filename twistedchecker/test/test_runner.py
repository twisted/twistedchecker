import sys
import StringIO
from twisted.trial import unittest

from twistedchecker.core.runner import Runner


class RunnerTestCase(unittest.TestCase):
    """
    Test for twistedchecker.core.runner.Runner .
    """

    def setUp(self):
        """
        Redirect stdout to a temp C{StringIO} stream
        """
        self.outputStream = StringIO.StringIO()
        self.patch(sys, "stdout", self.outputStream)


    def test_run(self):
        """
        Pass argument "--version" to C{runner.run}, and it should show
        a version infomation, then exit.
        """
        runner = Runner()
        runner.setOutput(self.outputStream)
        self.assertRaises(SystemExit, runner.run, ["--version"])
