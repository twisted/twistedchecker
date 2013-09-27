# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test cases for running the functional tests in
L{twistedchecker.functionaltests}.
"""
from functools import update_wrapper

from twisted.trial import unittest



def functionalTester(testCase, a, b):
    testCase.assertEqual(a, b)



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



def tests():
    t = []
    x = iter([1,2,3,4,5,6])
    for i in x:
        i2 = next(x)
        t.append(
            ('test_foo%s' % (i,), _partial2(functionalTester, a=i, b=i2)))
    return dict(t)



FunctionalTests = type(
    "FunctionalTests",
    (unittest.TestCase,),
    tests()
)
