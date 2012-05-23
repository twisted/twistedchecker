import StringIO
from twisted.trial import unittest

from twistedchecker.core.runner import Runner

class RunnerTestCase(unittest.TestCase):
  def testRun():
    resultOutput = StringIO.StringIO()
    runner = Runner()
    runner.setOutput(resultOutput)
    runner.run([])
    self.failUnless(len(resultOutput),"Fail to get result from runner")