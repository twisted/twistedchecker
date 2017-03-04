import ast
import os

class PatternFinder(ast.NodeVisitor):

    def __init__(self):
        """
        Initialize two lists to save patterns.
        """
        self.patternsFunc = set([])
        self.patternsClass = set([])


    def visit_Call(self, nodeCall):
        """
        Be invoked when visiting a node of function call.

        @param node: currently visiting node
        """
        super(PatternFinder, self).generic_visit(nodeCall)
        # Capture assignment like 'f = getattr(...)'.
        if hasattr(nodeCall.func, "func"):
            # In this case, the statement should be
            # 'f = getattr(...)()'.
            nodeCall = nodeCall.func
        # Make sure the function's name is 'getattr'.
        if not hasattr(nodeCall.func, "id"):
            return
        if nodeCall.func.id != "getattr":
            return

        # Capture 'f = getattr(foo, "bar_%s" % baz )' or
        # 'f = getattr(foo, "bar_" + baz )'.
        nodeArgument = nodeCall.args[1]
        if not isinstance(nodeArgument, ast.BinOp):
            return
        operation = nodeArgument.op
        if type(operation) not in [ast.Mod, ast.Add]:
            return
        nodePattern = nodeArgument.left
        if not isinstance(nodePattern, ast.Str):
            return
        pattern = nodePattern.s
        if not ((type(operation) == ast.Add and pattern.endswith("_")) or
                (pattern.count("%s") == 1 and pattern.endswith("_%s"))):
            return
        pattern = pattern.replace("%s", "")
        if pattern[:1].isalpha() and not pattern[:1].islower():
            self.patternsClass.add(pattern)
        else:
            self.patternsFunc.add(pattern)



def findPatternsInFile(codes, patternFinder):
    """
    Find patterns of exceptions in a file.

    @param codes: code of the file to check
    @param patternFinder: a visitor for pattern checking and save results
    """
    tree = ast.parse(codes)
    patternFinder.visit(tree)



def findAllExceptions(pathToCheck):
    """
    Find patterns of exceptions in a file or folder.

    @param patternFinder: a visitor for pattern checking and save results
    @return: patterns of special functions and classes
    """
    finder = PatternFinder()
    if os.path.isfile(pathToCheck):
        with open(pathToCheck) as f:
            findPatternsInFile(f.read(), finder)
    else:
        for path, dirs, files in os.walk(pathToCheck):
            for file in files:
                _, extname = os.path.splitext(file)
                if extname == ".py":
                    pathFile = os.path.join(path, file)
                    with open(pathFile) as f:
                        findPatternsInFile(f.read(), finder)
    return finder.patternsFunc, finder.patternsClass
