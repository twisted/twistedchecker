"""
Utility functions for twistedchecker.
"""

def isTestModule(modulename):
    """
    Determine whether a module is a test module
    by given module name.
    """
    filename = modulename.split('.')[-1]
    return ".test." in modulename and filename.startswith('test')



def moduleNeedsTests(modulename):
    """
    Determine whether a module is a is a special module.
    like __init__
    """
    return not modulename.split(".")[-1].startswith("_")



__all__ = ["isTestModule", "moduleNeedsTests"]
