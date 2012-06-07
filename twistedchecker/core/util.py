"""
Utility functions for twistedchecker.
"""

def isTestModule(modulename):
    """
    Determine whether a module is a test module
    by given module name.
    """
    return ".test." in modulename



def isSpecialModule(modulename):
    """
    Determine whether a module is a is a special module.
    like __init__
    """
    return modulename.split(".")[-1].startswith("_")



__all__ = ["isTestModule", "isSpecialModule"]
