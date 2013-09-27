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

from twistedchecker.core.runner import Runner
from twistedchecker.reporters.test import TestReporter



def _partial2(wrapped, *partialArgs, **partialKwargs):
    """
    A custom implementation of L{functools.partial} which returns a function
    instead of a partial object.  This allows it to be assigned to a class
    attribute and used as an instance method.

    @param wrapped: The function whose arguments will be partially applied
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
        return wrapped(*args, **kwargs)
    return update_wrapper(wrapper, wrapped)



def _formatResults(moduleName, expectedResult, actualResult):
    """
    Format the results side by side for easy comparison
    """
    i = itertools.izip_longest(
        ['= Expected ='] + expectedResult.splitlines(),
        ['= Actual ='] + actualResult.splitlines(), fillvalue='')

    output = ['', moduleName]
    for col1, col2 in i:
        output.append(col1.ljust(20) + col2)
    return os.linesep.join(output)




def _parseLimitMessages(testfile):
    """
    The first line of testfile should in format of:
    # enable/disable: [Message ID], ...

    @param testfile: testfile to read, enable and disable infomation should
        in the first line of it.
    """
    firstline = open(testfile).readline()
    if "enable" not in firstline and "disable" not in firstline:
        # Could not find enable or disable messages
        return
    action, messages = firstline.lstrip("#").strip().split(":", 1)
    messages = [msgid for msgid in messages.strip().split(",") if msgid]
    action = action.strip()

    return action, messages



def _setLinterLimits(linter, action, messages):
    if action == "enable":
        # Disable all other messages
        linter.disable_noerror_messages()

    messageModifier = getattr(linter, action)
    for msgid in messages:
        messageModifier(msgid)



def _runTest(testCase, testFilePath):
    """
    Run a functional test.

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

    runner.run([moduleName])

    # Check the results
    expectedResult = open(pathResultFile).read()
    outputResult = outputStream.getvalue()

    try:
        testCase.assertEqual(expectedResult, outputResult)
    except unittest.FailTest:
        testCase.fail(_formatResults(moduleName, expectedResult, outputResult))

# Enable pep8 checking
# pep8Checker = _getChecker(runner, "pep8")
# if pep8Checker:
#     pep8Checker.pep8Enabled = True
# Run the test


def tests():
    t = []
    t.append(
        ('test_foo',
         _partial2(
             _runTest,
             testFilePath=('/home/richard/projects/TwistedChecker/'
                           'branches/isolated-functional-tests-1010392/'
                           'twistedchecker/functionaltests/argumentname.py')))
    )
    return dict(t)



FunctionalTests = type(
    "FunctionalTests",
    (unittest.TestCase,),
    tests()
)
