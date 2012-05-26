import sys
import os
import StringIO

from twisted.trial import unittest

import twistedchecker
from twistedchecker.core.runner import Runner


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
        self.resultMessages = None


    def hackMethodAddMessage(self, msg_id, location, msg):
        """
        This hack method will replace C{add_message} in the reporter
        of C{PyLinter}, and record check results

        @param msg_id: message id
        @param location: detailed location information
        @param msg: text message
        """
        assert self.currentRunner, "could not find the runner currently using"
        reporter = self.currentRunner.linter.reporter
        module, obj, line, col_offset = location[1:]
        if module not in reporter._modules:
            if module:
                reporter.writeln('************* Module %s' % module)
                reporter._modules[module] = 1
            else:
                reporter.writeln('************* %s' % module)
        if obj:
            obj = ':%s' % obj
        if reporter.include_ids:
            sigle = msg_id
        else:
            sigle = msg_id[0]
        self.resultMessages["line:%s" % line] = msg_id
        reporter.writeln('%s:%3s,%s%s: %s' %
                         (sigle, line, col_offset, obj, msg))


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
            # record currently using runner.
            self.currentRunner = runner
            # replace the add_message method of the reporter to
            # C{RunnerTestCase.hackMethodAddMessage}.
            runner.linter.reporter.add_message = self.hackMethodAddMessage
            runner.run(["twistedchecker.functionaltests.%s" % testfile])
            # check if the results
            for line in self.configFunctionalTest[testfile]:
                predictResult = self.configFunctionalTest[testfile][line]
                predictResult.setdefault("msgid", None)
                if predictResult["shouldfail"] and predictResult["msgid"]:
                    # the test should fail with a specified message id
                    self.assertTrue(line in self.resultMessages and
                        predictResult["msgid"] == self.resultMessages[line],
                        msg="%s in %s should fail with a message %s, got %s" %
                            (line, testfile, predictResult["msgid"],
                             self.resultMessages[line]))
                elif predictResult["shouldfail"]:
                    # the test should fail
                    self.assertTrue(line in self.resultMessages,
                        msg="%s in %s should fail" % (line, testfile))
                else:
                    # the test should pass
                    self.assertTrue(line not in self.resultMessages,
                        msg="%s in %s should pass" % (line, testfile))
            print >> sys.stderr, "\tchecked test file: %s.py\n" % testfile
        print >> sys.stderr, "\t----------------\n"
