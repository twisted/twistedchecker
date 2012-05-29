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
    debug = False

    def setUp(self):
        """
        Redirect stdout to a temp C{StringIO} stream.
        """
        self.outputStream = StringIO.StringIO()
        self.patch(sys, "stdout", self.outputStream)


    def _removeSpaces(self,str):
        """
        Remove whitespaces in str.

        @param: a string
        """
        return str.strip().replace(" ","")


    def _limitMessages(self, testfile, runner):
        """
        Enable or disable messages according to the testfile.
        The first line of testfile should in format of:
        # enable/disable: [Message ID], ...

        @param testfile: testfile to read, enable and disable infomation should
        in the first line of it.
        @param runner: current runner for checking testfile.
        """
        firstline = open(testfile).readline()
        if "enable" not in firstline and "disable" not in firstline:
            # could not find enable or disable messages
            return
        action,messages = firstline.strip("#").strip().split(":")
        messages = self._removeSpaces(messages).split(",")
        action = action.strip()

        if action == "enable":
            # disable all other messages
            runner.linter.disable_noerror_messages()
            for msgid in messages:
                if not msgid:
                    continue
                runner.linter.enable(msgid)
        else:
            for msgid in messages:
                if not msgid:
                    continue
                runner.linter.disable(msgid)


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
        pathInputTestFiles = os.path.join(twistedchecker.abspath,
                                          "functionaltests",
                                          "input")
        testfiles = [file for file in os.listdir(pathInputTestFiles)
                     if file.endswith(".py") and file != "__init__.py"]
        for testfile in testfiles:
            pathTestFile = os.path.join(twistedchecker.abspath, "functionaltests",
                                      "input", testfile)
            resultfile = testfile.replace(".py",".txt")
            pathResultFile = os.path.join(twistedchecker.abspath, "functionaltests",
                                      "results", resultfile)
            self.assertTrue(os.path.exists(pathTestFile),
                       msg="could not find testfile: %s" % testfile)
            self.assertTrue(os.path.exists(pathResultFile),
                       msg="could not find resultfile: %s" % resultfile)
            # clear output stream and check results.
            self.outputStream.truncate(0)
            runner = Runner()
            runner.setOutput(self.outputStream)
            # set the reporter to C{twistedchecker.reporters.test.TestReporter}
            runner.setReporter(TestReporter())
            self._limitMessages(pathTestFile,runner)
            runner.run(["twistedchecker.functionaltests.input.%s" % testfile.replace(".py","")])
            # check the results
            if self.debug:
                print >> sys.stderr, self.outputStream.getvalue()
            predictResult = self._removeSpaces(open(pathResultFile).read())
            outputResult = self._removeSpaces(self.outputStream.getvalue())
            self.assertEqual(outputResult,predictResult,
                             "Incorrect result of %s, should be:\n---\n%s\n---" % \
                             (testfile,predictResult))
            print >> sys.stderr, "\tchecked test file: %s\n" % testfile
        print >> sys.stderr, "\t----------------\n"
