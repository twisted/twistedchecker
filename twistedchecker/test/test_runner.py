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


    def clearOutputStream(self):
        """
        A function to clear output stream.
        """
        self.outputStream = StringIO.StringIO()


    def _removeSpaces(self, str):
        """
        Remove whitespaces in str.

        @param: a string
        """
        return str.strip().replace(" ", "")


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
        action, messages = firstline.strip("#").strip().split(":")
        messages = self._removeSpaces(messages).split(",")
        messages = [msgid for msgid in messages if msgid]
        action = action.strip()

        if action == "enable":
            # disable all other messages
            runner.linter.disable_noerror_messages()
            for msgid in messages:
                runner.linter.enable(msgid)
        else:
            for msgid in messages:
                runner.linter.disable(msgid)


    def test_run(self):
        """
        Pass argument "--version" to C{runner.run}, and it should show
        a version infomation, then exit. So that I could know it called pylint.
        """
        self.clearOutputStream()
        runner = Runner()
        runner.setOutput(self.outputStream)
        self.assertRaises(SystemExit, runner.run, ["--version"])
        self.assertTrue(self.outputStream.getvalue().count("Python") > 0, \
                        msg="failed to call pylint")


    def listAllTestModules(self):
        """
        Get all functional test modules.
        """
        testmodules = []
        pathTestModules = os.path.join(twistedchecker.abspath,
                                       "functionaltests")
        for root, dirs, files in os.walk(pathTestModules):
            for testfile in files:
                if testfile.endswith(".py") and testfile != "__init__.py":
                    pathFile = os.path.join(twistedchecker.abspath,
                                            root, testfile)
                    pathRelative = os.path.relpath(pathFile,
                                                   twistedchecker.abspath)
                    modulename = "twistedchecker." + \
                                 pathRelative.strip(".py").replace(os.sep, ".")
                    testmodules.append((pathFile, modulename))
        return testmodules


    def test_functions(self):
        """
        This will automatically test some functional test files
        controlled by C{RunnerTestCase.configFunctionalTest}.
        """
        print >> sys.stderr, "\n\t----------------"
        testmodules = self.listAllTestModules()
        for pathTestFile, modulename in testmodules:
            pathResultFile = pathTestFile.replace(".py", ".result")
            self.assertTrue(os.path.exists(pathTestFile),
                       msg="could not find testfile:\n%s" % pathTestFile)
            self.assertTrue(os.path.exists(pathResultFile),
                       msg="could not find resultfile:\n%s" % pathResultFile)
            self.clearOutputStream()
            runner = Runner()
            runner.setOutput(self.outputStream)
            # set the reporter to C{twistedchecker.reporters.test.TestReporter}
            runner.setReporter(TestReporter())
            self._limitMessages(pathTestFile, runner)
            runner.run([modulename])
            # check the results
            if self.debug:
                print >> sys.stderr, self.outputStream.getvalue()
            predictResult = self._removeSpaces(open(pathResultFile).read())
            outputResult = self._removeSpaces(self.outputStream.getvalue())
            self.assertEqual(outputResult, predictResult,
                 "Incorrect result of %s, should be:\n---\n%s\n---" % \
                 (modulename, predictResult))
            print >> sys.stderr, "\t%s\n" % modulename
        print >> sys.stderr, "\t----------------\n"
