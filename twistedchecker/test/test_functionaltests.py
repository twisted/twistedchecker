# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test cases for running the functional tests in
L{twistedchecker.functionaltests}.
"""

from functools import update_wrapper
import io
import itertools
import os

from twisted.python.reflect import filenameToModuleName
from twisted.trial import unittest

import twistedchecker
from twistedchecker.core.runner import Runner
from twistedchecker.reporters.test import TestReporter

try:
    from itertools import zip_longest
    from io import StringIO
except:
    from itertools import izip_longest as zip_longest
    from StringIO import StringIO



def _partial2(wrapped, *partialArgs, **partialKwargs):
    """
    A custom implementation of L{functools.partial} which returns a function
    instead of a partial object.  This allows it to be assigned to a class
    attribute and used as an instance method.

    @see: U{https://twistedmatrix.com/trac/ticket/2645}
    @see: U{http://bugs.python.org/issue4331}

    @param wrapped: The function whose arguments will be partially applied.
    @type wrapped: L{callable}

    @param partialArgs: The positional arguments which will be applied to
        C{wrapped}.
    @type partialArgs: L{tuple}

    @param partialKwargs: The keyword arguments which will be applied to
        C{wrapped}.
    @type partialKwargs: L{dict}

    @return: A wrapper function which will apply the supplied arguments to
        C{wrapped} when it is called.
    @rtype: L{callable}
    """
    def wrapper(*args, **kwargs):
        args = args + partialArgs[len(args):]
        kwargs.update(partialKwargs)
        wrapped(*args, **kwargs)
    return update_wrapper(wrapper, wrapped)



def _formatResults(moduleName, expectedResult, actualResult):
    """
    Format the expected and actual results side by side for easy comparison.

    @param moduleName: The fully qualified module name.
    @type moduleName: L{str}

    @param expectedResult: The expected I{twistedchecker} output.
    @type expectedResult: L{str}

    @param actualResult: The actual I{twistedchecker} output.
    @type actualResult: L{str}

    @return: The expected and actual output formatted in two columns with
        headings.
    @rtype: L{str}
    """
    i = zip_longest(
        ['= Expected ='] + expectedResult,
        ['= Actual ='] + actualResult,
        fillvalue='')

    output = ['', moduleName]
    for col1, col2 in i:
        output.append(col1.ljust(20) + col2)
    return os.linesep.join(output)



def _parseLimitMessages(testFilePath):
    """
    Parse a test module file for a message control header.

    The first line of testfile should in format of:
    enable/disable: [Message ID], ...

    @param testFilePath: test module file to read.
    @type testFilePath: L{str}

    @return: A 2-tuple of (C{action}, C{messages}) where C{action} is either
        C{"enable"} or C{"disable"} and C{messages} is a list of
        I{twistedchecker} message IDs.
    @rtype: L{tuple}
    """
    firstline = open(testFilePath).readline()
    if "enable" not in firstline and "disable" not in firstline:
        # Could not find enable or disable messages
        return
    action, messages = firstline.lstrip("#").strip().split(":", 1)
    messages = [msgid for msgid in messages.strip().split(",") if msgid]
    action = action.strip()

    return action, messages



def _setLinterLimits(linter, action, messages):
    """
    Enable or disable the reporting of certain linter messages.

    @param linter: The linter whose
        L{twistedchecker.checkers.pep8format.PEP8Checker} will be enabled.
    @type linter: L{pylint.lint.PyLinter}

    @param action: Either C{"enable"} or C{"disable"}.
    @type action: L{str}

    @param messages: A list of twistedchecker message IDs to be enabled or
        disabled.
    @type messages: L{list} of L{str}
    """
    if action == "enable":
        # Disable all other messages
        linter.disable_noerror_messages()

    messageModifier = getattr(linter, action)
    for msgid in messages:
        messageModifier(msgid)



def _enablePEP8Checker(linter):
    """
    Enable PEP8 checking on the twistedchecker linter.

    @param linter: The linter whose
        L{twistedchecker.checkers.pep8format.PEP8Checker} will be enabled.
    @type linter: L{pylint.lint.PyLinter}
    """
    checkers = linter.get_checkers()
    for checker in checkers:
        if getattr(checker, "name", None) == "pep8":
            checker.pep8Enabled = True
            return
    else:
        raise RuntimeError('pep8 checker not found in ', checkers)



def _runTest(testCase, testFilePath):
    """
    Run a functional test.

    @param testCase: The test case on which to call assertions.
    @type testCase: L{unittest.TestCase}

    @param testFilePath: The path to the module to test.
    @type testFilePath: L{str}
    """
    pathResultFile = testFilePath.replace(".py", ".result")
    moduleName = filenameToModuleName(testFilePath)
    outputStream = io.BytesIO()

    runner = Runner()
    runner.allowOptions = False
    runner.setOutput(outputStream)
    runner.setReporter(TestReporter())

    limits = _parseLimitMessages(testFilePath)
    if limits is not None:
        action, messages = limits
        _setLinterLimits(runner.linter, action, messages)

    _enablePEP8Checker(runner.linter)

    exitCode = None
    try:
        runner.run([moduleName])
    except SystemExit as error:
        exitCode = error.code

    # Check the results
    with open(pathResultFile) as f:
        expectedResult = sorted(f.read().strip().splitlines())

    outputResult = sorted(outputStream.getvalue().strip().splitlines())

    try:
        testCase.assertEqual(expectedResult, outputResult)
    except unittest.FailTest:
        testCase.fail(_formatResults(moduleName, expectedResult, outputResult))

    if not expectedResult:
        testCase.assertEqual(0, exitCode)
    else:
        testCase.assertNotEqual(0, exitCode)



def _testNameFromModuleName(moduleName):
    """
    Mangle a module name so it can be used as a test function name.

    @param moduleName: The qualified module name.
    @type moduleName: L{str}

    @return: The test name derived from the supplied C{moduleName}.
    @rtype: L{str}
    """
    return 'test_' + moduleName.replace('.', '_')



def _testModules():
    """
    Discover all the functional test modules.

    Modules whose name begin with an underscore are ignored.

    @return: An iterator of test module file paths.
    @rtype: L{iter}
    """
    pathTestModules = os.path.join(twistedchecker.abspath, "functionaltests")
    for root, dirs, files in os.walk(pathTestModules):
        for testfile in files:
            if testfile.startswith("_"):
                continue
            if testfile.endswith(".py"):
                yield os.path.join(twistedchecker.abspath, root, testfile)



def _testsForModules(testModules):
    """
    Return a dictionary of test names and test functions.

    @param testModules: An iterable list of functional test module names.
    @type testModules: L{iter}

    @return: A dictionary of test functions keyed by test name.
    @rtype: L{dict} of (L{str}, L{callable})
    """
    t = []
    for modulePath in testModules:
        moduleName = filenameToModuleName(modulePath)
        t.append(
            (_testNameFromModuleName(moduleName),
             _partial2(_runTest, testFilePath=modulePath))
        )
    return dict(t)



# Create a TestCase class using a dictionary of dynamically generated test
# methods.
FunctionalTests = type(
    "FunctionalTests",
    (unittest.TestCase,),
    _testsForModules(_testModules())
)
