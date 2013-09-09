# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test cases for running the functional tests in
L{twistedchecker.functionaltests}.
"""

import itertools
import os
import StringIO

from twisted.trial import unittest

import twistedchecker
from twistedchecker.core.runner import Runner
from twistedchecker.reporters.test import TestReporter



def _removeSpaces(str):
    """
    Remove whitespaces in str.

    @param str: a string
    @return: The stripped string
    """
    return str.strip().replace(" ", "")



def listAllTestModules():
    """
    Discover all the functional test modules.

    Modules whose name begin with an underscore are ignored.

    @return: A list of test file paths and module names
    @rtype: L{list} of 2-L{tuple}(L{str}, L{str})
    """
    testmodules = []
    pathTestModules = os.path.join(twistedchecker.abspath,
                                   "functionaltests")
    for root, dirs, files in os.walk(pathTestModules):
        for testfile in files:
            if testfile.startswith("_"):
                continue
            if testfile.endswith(".py"):
                pathFile = os.path.join(twistedchecker.abspath,
                                        root, testfile)
                pathRelative = os.path.relpath(pathFile,
                                               twistedchecker.abspath)
                modulename = "twistedchecker." + \
                    pathRelative.replace(".py", "").replace(os.sep, ".")
                testmodules.append((pathFile, modulename))
    return testmodules



def _limitMessages(testfile, runner):
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
        # Could not find enable or disable messages
        return
    action, messages = firstline.strip("#").strip().split(":")
    messages = _removeSpaces(messages).split(",")
    messages = [msgid for msgid in messages if msgid]
    action = action.strip()

    if action == "enable":
        # Disable all other messages
        runner.linter.disable_noerror_messages()
        for msgid in messages:
            runner.linter.enable(msgid)
    else:
        for msgid in messages:
            runner.linter.disable(msgid)



def _getChecker(runner, checkerName):
    """
    Get a specified checker from a Runner object.

    @param runner: an instance of Runner
    @param checkerName: the name of a checker
    @return: a checker object
    """
    for checker in runner.linter.get_checkers():
        if hasattr(checker, "name") and checker.name == checkerName:
            return checker
    return None



def _testNameFromModuleName(moduleName):
    """
    Mangle a module name so it can be used as a test function name.

    @param moduleName: The qualified module name.
    @type moduleName: L{str}

    @return: The test name derived from the supplied C{moduleName}.
    @rtype: L{str}
    """
    return 'test_' + moduleName.replace('.', '_')



def _buildTestMethod(testFilePath, moduleName):
    """
    Create a closure function which will call C{_runTest} on its
    parent instance, supplying the arguments enclosed in this function
    call.

    @param testFilePath: The path to the sample module to test.
    @type testFilePath: L{str}

    @param moduleName: The qualified module name.
    @type moduleName: L{str}

    @return: The closure function
    @rtype: L{function}
    """
    return lambda self: self._runTest(testFilePath, moduleName)



def _addFunctionalTests(testCaseClass):
    """
    Discover functional test modules and add test methods to a
    TestCase class for each discovered functional test.

    These test methods can be discovered and run individually by
    trial.

    @param testCaseClass: The class to which test methods will be
        added.
    @type testCaseClass: L{type}

    @return: The modified C{testCaseClass}
    @rtype: L{type}
    """
    for testFilePath, moduleName in listAllTestModules():
        setattr(
            testCaseClass,
            _testNameFromModuleName(moduleName),
            _buildTestMethod(testFilePath, moduleName)
            )
    return testCaseClass


@_addFunctionalTests
class FunctionalTests(unittest.TestCase):
    """
    A TestCase to which functional test methods will be dynamically
    added at module load time.
    """
    def _runTest(self, testFilePath, moduleName):
        """
        Run a functional test.

        @param testFilePath: The path to the module to test.
        @type testFilePath: L{str}

        @param moduleName: The qualified name of the module to test.
        @type moduleName: L{str}
        """
        pathResultFile = testFilePath.replace(".py", ".result")

        self.assertTrue(
            os.path.exists(testFilePath),
            msg="could not find testfile: %r" % (testFilePath,))
        self.assertTrue(
            os.path.exists(pathResultFile),
            msg="could not find resultfile: %r" % (pathResultFile,))

        outputStream = StringIO.StringIO()
        runner = Runner()
        runner.allowOptions = False
        runner.setOutput(outputStream)

        # Set the reporter to
        # C{twistedchecker.reporters.test.TestReporter}
        runner.setReporter(TestReporter())
        _limitMessages(testFilePath, runner)

        # Enable pep8 checking
        pep8Checker = _getChecker(runner, "pep8")
        if pep8Checker:
            pep8Checker.pep8Enabled = True

        # Run the test
        runner.run([moduleName])

        # Check the results
        expectedResult = _removeSpaces(
            open(pathResultFile).read()).splitlines()
        outputResult = _removeSpaces(
            outputStream.getvalue()).splitlines()

        try:
            self.assertEqual(expectedResult, outputResult)
        except unittest.FailTest:
            # Format the results side by side for easy comparison
            i = itertools.izip_longest(
                ['= Expected ='] + expectedResult,
                ['= Actual ='] + outputResult, fillvalue='')

            output = ['', moduleName]
            for col1, col2 in i:
                output.append(col1.ljust(20) + col2)
            output.append('')

            self.fail('\n'.join(output))
