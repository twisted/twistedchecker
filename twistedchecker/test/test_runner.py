import sys
import os
import StringIO

from twisted.trial import unittest

import twistedchecker
from twistedchecker.core.runner import Runner
from twistedchecker.reporters.test import TestReporter


class RunnerTestCase(unittest.TestCase):
    """
    Test for twistedchecker.core.runner.Runner.
    """
    configFunctionalTest = {
        "indentation": {
             "line:4": {"shouldfail": False},
             "line:8": {"shouldfail": True, "msgid": "W0311"},
            "line:12": {"shouldfail": True, "msgid": "W0312"},
        }
    }


    def setUp(self):
        """
        Redirect stdout to a temp C{StringIO} stream.
        """
        self.outputStream = StringIO.StringIO()
        self.patch(sys, "stdout", self.outputStream)
        self.currentRunner = None


    def test_run(self):
        """
        Pass argument "--version" to C{runner.run}, and it should show
        a version infomation, then exit. So that I could know it called pylint.
        """
        # clear output stream
        self.outputStream.truncate(0)
        runner = Runner()
        runner.setOutput(self.outputStream)
        self.assertRaises(SystemExit, runner.run, ["--version"])
        self.assertTrue(self.outputStream.getvalue().count("Python") > 0, \
                        msg="failed to call pylint")


    def test_functions(self):
        """
        This will automatically test some functional test files
        controlled by C{RunnerTestCase.configFunctionalTest}.
        """
        print >> sys.stderr, "\n\t----------------"
        for testfile in self.configFunctionalTest:
            pathTestFile = os.path.join(twistedchecker.abspath,
                                        "functionaltests", "%s.py" % testfile)
            self.assertTrue(os.path.exists(pathTestFile),
                       msg="could not find testfile: %s.py" % testfile)
            # clear output stream and check results.
            self.outputStream.truncate(0)
            self.resultMessages = {}
            runner = Runner()
            runner.setOutput(self.outputStream)
            testreporter = TestReporter()
            runner.setReporter(testreporter)
            # record currently using runner.
            self.currentRunner = runner
            # set the reporter to C{twistedchecker.reporters.test.TestReporter}

            # C{RunnerTestCase.hackMethodAddMessage}.
            runner.run(["twistedchecker.functionaltests.%s" % testfile])
            # check if the results
            for line in self.configFunctionalTest[testfile]:
                predictResult = self.configFunctionalTest[testfile][line]
                predictResult.setdefault("msgid", None)
                if predictResult["shouldfail"] and predictResult["msgid"]:
                    # the test should fail with a specified message id
                    self.assertTrue(line in testreporter.resultMessages and
                        predictResult["msgid"] ==
                            testreporter.resultMessages[line],
                        msg="%s in %s should fail with a message %s, got %s" %
                            (line, testfile, predictResult["msgid"],
                             testreporter.resultMessages[line]))
                elif predictResult["shouldfail"]:
                    # the test should fail
                    self.assertTrue(line in testreporter.resultMessages,
                        msg="%s in %s should fail" % (line, testfile))
                else:
                    # the test should pass
                    self.assertTrue(line not in testreporter.resultMessages,
                        msg="%s in %s should pass" % (line, testfile))
            print >> sys.stderr, "\tchecked test file: %s.py\n" % testfile
        print >> sys.stderr, "\t----------------\n"
