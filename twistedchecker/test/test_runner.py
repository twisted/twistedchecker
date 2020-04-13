# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twistedchecker.core.runner}.
"""

import sys
import os
import operator

from functools import reduce

from pylint.reporters.text import TextReporter

from io import StringIO

from twisted.trial import unittest

import twistedchecker
from twistedchecker.core.runner import Runner
from twistedchecker.checkers.header import HeaderChecker

from twistedchecker.test.test_exceptionfinder import (
    createTestFiles as createTestFilesForFindingExceptions)



class RunnerTestCase(unittest.TestCase):
    """
    Test for twistedchecker.core.runner.Runner.
    """
    debug = False

    def setUp(self):
        """
        Redirect stdout to a temp C{StringIO} stream.
        """
        self.outputStream = StringIO()
        self.patch(sys, "stdout", self.outputStream)
        self.errorStream = StringIO()
        self.patch(sys, "stderr", self.errorStream)


    def clearOutputStream(self):
        """
        A function to clear output stream.
        """
        self.outputStream = StringIO()


    def makeRunner(self):
        """
        Return a runner instance.
        """
        runner = Runner()
        runner.setOutput(self.outputStream)
        return runner


    def _loadAllowedMessages(self):
        """
        Load allowed messages from test files.
        """
        pathTests = os.path.join(twistedchecker.abspath, "functionaltests")
        testfiles = reduce(operator.add,
                           [[os.path.join(pathDir, f) for f in files if f.endswith(".py")]
                            for pathDir, _, files in os.walk(pathTests)])
        messagesAllowed = set(Runner.allowedMessagesFromPylint)
        for testfile in testfiles:
            with open(testfile) as f:
                firstline = f.readline().strip()
            if (firstline.startswith("#") and "enable" in firstline
                                          and ":" in firstline):
                messages = firstline.split(":")[1].strip().split(",")
                messagesAllowed.update(messages)
        return messagesAllowed


    def test_findUselessCheckers(self):
        """
        Test for method findUselessCheckers
        """
        runner = Runner()
        registeredCheckers = sum(list(runner.linter._checkers.values()), [])
        # remove checkers other than header checker
        headerCheckerList = [ckr
                             for ckr in registeredCheckers
                             if type(ckr) == HeaderChecker]
        self.assertTrue(headerCheckerList)
        headerChecker = headerCheckerList[0]
        uselessCheckers = runner.findUselessCheckers(
                            list(headerChecker.msgs.keys())[:1])
        self.assertEqual(len(uselessCheckers) + 1, len(registeredCheckers))
        self.assertTrue(headerChecker not in uselessCheckers)


    def test_unregisterChecker(self):
        """
        Test for method unregisterChecker.

        Remove HeaderChecker from registered,
        and make sure it was removed.
        """
        runner = Runner()
        registeredCheckers = sum(list(runner.linter._checkers.values()), [])
        # Make sure an instance of HeaderChecker in registered checkers
        headerCheckerList = [ckr
                             for ckr in registeredCheckers
                             if type(ckr) == HeaderChecker]
        self.assertTrue(headerCheckerList)
        headerChecker = headerCheckerList[0]
        # Make sure it in option providers
        self.assertTrue(headerChecker in runner.linter.options_providers)
        runner.unregisterChecker(headerChecker)
        # Make sure the instance of HeaderChecker was removed
        registeredCheckers = sum(list(runner.linter._checkers.values()), [])
        self.assertFalse(headerChecker in registeredCheckers)
        # Could not check reports because HeaderChecker is not be
        # recorded in that list
        # Make sure it was removed from option providers
        self.assertFalse(headerChecker in runner.linter.options_providers)


    def test_restrictCheckers(self):
        """
        Test for method restrictCheckers.

        Manually set allowed messages,
        then check for the result of registered checkers
        after run this method.
        """
        runner = Runner()
        runner.restrictCheckers(list(HeaderChecker.msgs.keys())[:1])
        # After run it, only HeaderChecker should be left in
        # registered checkers
        registeredCheckers = sum(list(runner.linter._checkers.values()), [])
        self.assertEqual(len(registeredCheckers), 1)
        self.assertEqual(type(registeredCheckers[0]), HeaderChecker)


    def test_allMessagesAreRegistered(self):
        """
        A test to assume all tests are registered to reporter.
        """
        linter = Runner().linter
        messagesFromTests = self._loadAllowedMessages()
        messagesFromReporter = linter.reporter.messagesAllowed
        messagesDisabled = set(linter
                           .cfgfile_parser.get("TWISTEDCHECKER", "disable")
                           .replace(" ", "").split(","))
        self.assertEqual(messagesFromTests - messagesDisabled,
                         messagesFromReporter)


    def test_runVersion(self):
        """
        Pass argument "--version" to C{runner.run}, and it should show
        a version infomation, then exit. So that I could know it called pylint.
        """
        runner = Runner()
        runner.setOutput(self.outputStream)

        exitResult = self.assertRaises(SystemExit, runner.run, ["--version"])

        self.assertTrue(self.outputStream.getvalue().count("Python") > 0, \
                        msg="failed to call pylint")
        self.assertIsNone(runner.diffOption)
        self.assertEqual(0, exitResult.code)


    def test_runNoError(self):
        """
        When checked file is clean and has no errors it exit with code 0
        without any other output.
        """
        runner = Runner()
        runner.setOutput(self.outputStream)

        # The twistedchecker/checkers/__init__.py is assumed to be clean.
        exitResult = self.assertRaises(SystemExit, runner.run, [
            "twistedchecker.checkers.__init__"])

        self.assertEqual('', self.outputStream.getvalue())
        self.assertEqual(0, exitResult.code)


    def test_runWithErrors(self):
        """
        When checked file is not clean it will exit with non zero exit code.
        """
        runner = Runner()
        runner.setOutput(self.outputStream)

        # The comments functional test is assumed to have at lest one error.
        exitResult = self.assertRaises(SystemExit, runner.run, [
            "twistedchecker.functionaltests.comments"])

        self.assertNotEqual(0, exitResult.code)


    def test_parseWarnings(self):
        """
        Test for twistedchecker.core.runner.Runner.parseWarnings.
        """
        textWarnings = """
************* Module foo
W9001:  1,0: Missing copyright header
************* Module bar
W9002:  1,0: Missing a reference to test module in header
C0111:  10,0: Missing docstring
        """.strip()

        warningsCorrect = {
            "foo": {"W9001:  1,0: Missing copyright header", },
            "bar": {"W9002:  1,0: Missing a reference "
                    "to test module in header",
                    "C0111:  10,0: Missing docstring"
                   }
        }

        warnings = Runner().parseWarnings(textWarnings)
        self.assertEqual(warnings, warningsCorrect)

    def test_runDiffNoWarnings(self):
        """
        When running in diff mode set path to result file and exit with 0 if
        no warnings were found.
        """
        runner = self.makeRunner()
        # Mock showDiffResults to check that it is called.
        showDiffResultsCalls = []
        runner.showDiffResults = lambda: showDiffResultsCalls.append(True)

        exitResult = self.assertRaises(
            SystemExit,
            runner.run, ['--diff', 'path/to/previous.results', 'target'])

        self.assertEqual('path/to/previous.results', runner.diffOption)
        # Called once.
        self.assertEqual([True], showDiffResultsCalls)
        # Nothing in stderr or stdout.
        self.assertEqual('', self.outputStream.getvalue())
        self.assertEqual('', self.errorStream.getvalue())
        self.assertEqual(0, exitResult.code)


    def test_runDiffWarnings(self):
        """
        Exit with 1 when warnings are found in diff mode.
        """
        runner = self.makeRunner()
        runner.showDiffResults = lambda: 3

        exitResult = self.assertRaises(
            SystemExit,
            runner.run, ['--diff', 'path/to/previous.results', 'target'])

        self.assertEqual(1, exitResult.code)


    def test_showDiffResultsReadFail(self):
        """
        Show an error and exit with 1 when failing to read diff result file.
        """
        runner = self.makeRunner()
        runner.diffOption = 'no/such/file'

        result = runner.showDiffResults()

        self.assertEqual(1, result)
        self.assertEqual('', self.outputStream.getvalue())
        self.assertEqual(
            "Error: Failed to read result file 'no/such/file'.\n",
            self.errorStream.getvalue(),
            )

    def test_showDiffResultEmpty(self):
        """
        Return 0 when both sources are empty.
        """
        runner = self.makeRunner()
        runner.prepareDiff()
        runner._readDiffFile = lambda: ''

        result = runner.showDiffResults()

        self.assertEqual(0, result)
        self.assertEqual('', self.outputStream.getvalue())
        self.assertEqual('', self.errorStream.getvalue())


    def test_showDiffResultNoChanges(self):
        """
        Return 0 when both sources have same content.
        """
        runner = self.makeRunner()
        runner.prepareDiff()
        content = """
************* Module foo
W9001:  1,0: Missing copyright header
        """.strip()
        runner._readDiffFile = lambda: content
        runner.streamForDiff.write(content)

        result = runner.showDiffResults()

        self.assertEqual(0, result)
        self.assertEqual('', self.outputStream.getvalue())
        self.assertEqual('', self.errorStream.getvalue())


    def test_showDiffResultChanges(self):
        """
        Return 0 when both sources have same content.
        """
        runner = self.makeRunner()
        runner.prepareDiff()
        previous = """
************* Module foo
W9001:  1,0: Missing copyright header
        """.strip()
        new = """
************* Module foo
W9001:  1,0: Missing copyright header
W9001:  2,0: Missing copyright header
        """.strip()
        expectedOutput = """
************* Module foo
W9001:  2,0: Missing copyright header
""".lstrip()
        runner._readDiffFile = lambda: previous
        runner.streamForDiff.write(new)

        result = runner.showDiffResults()

        self.assertEqual(1, result)
        self.assertEqual(expectedOutput, self.outputStream.getvalue())
        self.assertEqual('', self.errorStream.getvalue())


    def test_formatWarnings(self):
        """
        Test for twistedchecker.core.runner.Runner.formatWarnings.
        """
        warnings = {
            "foo": {"W9001:  1,0: Missing copyright header", },
            "bar": {"W9002:  1,0: Missing a reference "
                    "to test module in header",
                    "C0111:  10,0: Missing docstring"
                   }
        }

        resultCorrect = """
************* Module bar
W9002:  1,0: Missing a reference to test module in header
C0111:  10,0: Missing docstring
************* Module foo
W9001:  1,0: Missing copyright header
        """.strip()

        result = Runner().formatWarnings(warnings)
        self.assertEqual(result, resultCorrect)


    def test_generateDiff(self):
        """
        Test for twistedchecker.core.runner.Runner.generateDiff.
        """
        oldWarnings = {
            "foo": {"W9001:  1,0: Missing copyright header"},
            "bar": {
                "W9002:  1,0: Missing a reference to test module in header",
                "C0111:  10,0: Missing docstring"
            }
        }

        newWarnings = {
            "foo": {
                "W9001:  1,0: Missing copyright header",
                "C0301: 10,0: Line too long"
            },
            "bar": {
                "W9002:  1,0: Missing a reference to test module in header",
                "C0111:  10,0: Missing docstring"
            },
            "baz": {
                "W9001:  1,0: Missing copyright header"
            }
        }

        diffCorrect = {
            "foo": {"C0301: 10,0: Line too long"},
            "baz": {"W9001:  1,0: Missing copyright header"}
        }

        # Make sure generated diff is correct.
        diff = Runner().generateDiff(oldWarnings, newWarnings)
        self.assertEqual(diff, diffCorrect)


    def test_getPathList(self):
        """
        Test for twistedchecker.core.runner.Runner.getPathList.
        """
        workingDir = os.getcwd()
        pathTwistedchecker = os.path.dirname(twistedchecker.__path__[0])
        inputList = [os.path.join("twistedchecker","functionaltests"),
                     "twistedchecker.core.util"]
        correctPaths = [os.path.join("twistedchecker","functionaltests"),
                        os.path.join("twistedchecker","core","util.py")]
        os.chdir(pathTwistedchecker)
        result = Runner().getPathList(inputList)
        # transform them to relative path.
        result = [os.path.relpath(path) for path in result]
        os.chdir(workingDir)

        self.assertEqual(result, correctPaths)


    def test_setNameExceptions(self):
        """
        Test for twistedchecker.core.runner.Runner.setNameExceptions.
        """
        pathTestFiles = createTestFilesForFindingExceptions(self.mktemp())
        self.clearOutputStream()
        runner = Runner()
        runner.setOutput(self.outputStream)

        runner.linter.set_reporter(TextReporter())
        runner.linter.config.msg_template = "{line}:{msg_id}"
        runner.linter.open()
        # Limit messages.
        runner.linter.disable_noerror_messages()
        # Enable invalid function names.
        runner.linter.enable("C0103")
        # Enable invalid method names.
        runner.linter.enable("C9302")

        workingDir = os.getcwd()
        os.chdir(os.path.dirname(pathTestFiles))
        moduleName = os.path.basename(pathTestFiles)

        exitResult = self.assertRaises(SystemExit, runner.run, [moduleName])

        os.chdir(workingDir)
        predictResult = "************* Module temp.test\n7:C9302\n11:C0103\n14:C0103\n15:C9302\n"
        outputResult = self.outputStream.getvalue()
        self.assertEqual(outputResult, predictResult)
        self.assertEqual(16, exitResult.code)
