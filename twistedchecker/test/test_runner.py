import sys
import StringIO
from twisted.trial import unittest

from twistedchecker.core.runner import Runner

class RunnerTestCase(unittest.TestCase):

    def testRun(self):
        resultOutput = StringIO.StringIO()
        stdout = sys.stdout
        sys.stdout = resultOutput
        runner = Runner()
        runner.setOutput(resultOutput)
        try:
            self.assertRaises(SystemExit,runner.run,["--version"])
            sys.stdout = stdout
        except:
            sys.stdout = stdout
            self.fail("Could not load runner")


