"""
Checker for python3 compatibility issues.
"""
import re

import logilab.astng.node_classes
from logilab.astng.exceptions import ASTNGError

from pylint.interfaces import IASTNGChecker
from pylint.checkers import BaseChecker



class Python3Checker(BaseChecker):
    """
    Checker for python3 compatibility issues.
    """

    __implements__ = (IASTNGChecker,)
    name = 'python3'
    msgs = {
     'W9601': ('For compatibility with python 3,'
               'you should import print_function from __future__',
               'Checking print statement for python 3.'),
     'W9602': ('dict.has_key() has been removed in python 3, '
               'use the in operator instead',
               'Checking has_key issue for python 3.'),
     'W9603': ('The built-in function apply is removed in python 3',
               'Checking apply issue for python 3.'),
     'W9604': ("Please use 'except Exception as e:',"
               "rather than 'except Exception, e:'",
               'Checking exception issue for python 3.'),
    }
    options = ()
    warningsOfCurrentModule = None
    linesOfCurrentModule = None

    def visit_module(self, node):
        """
        Save lines of the module currently checking.

        @param node: current node of checking
        """
        self.warningsOfCurrentModule = set([])
        self.linesOfCurrentModule = node.file_stream.readlines()


    def visit_print(self, node):
        """
        Be invoked when visiting a print statement.


        @param node: current node of checking
        """
        if self.warningsOfCurrentModule == None:
            return
        if "W9601" not in self.warningsOfCurrentModule:
            self.warningsOfCurrentModule.add("W9601")
            self.add_message('W9601', node=node.root())


    def visit_callfunc(self, node):
        """
        Be invoked when visiting a function node.

        @param node: current node of checking
        """
        self.checkHasKeyIssue(node)
        self.checkApplyIssue(node)


    def visit_tryexcept(self, node):
        """
        Be invoked when visiting a try...except node.

        @param node: current node of checking
        """
        self.checkExceptionIssue(node)


    def _getRawCodesInOneLine(self, node):
        """
        Get raw codes for given node, and put them into one line.

        @param node: node to check
        """
        linenoBegin = node.fromlineno - 1
        linenoEnd = node.tolineno - 1
        if (not self.linesOfCurrentModule or
            linenoEnd >= len(self.linesOfCurrentModule)):
            # in the case, the code is not from a module exists
            return None
        codeStatement = " ".join(
             [line.strip()
              for line in \
              self.linesOfCurrentModule[linenoBegin: linenoEnd + 1]])
        return codeStatement


    def checkExceptionIssue(self, node):
        """
        Check for exception issue in python 3(W9604).

        @param node: current node of checking
        """
        codeStatement = self._getRawCodesInOneLine(node)
        regexDeprecated = r"except\s+(\(.+\)|\w+)\s*,\s*\w+\:"
        if re.search(regexDeprecated, codeStatement):
            self.add_message('W9604', node=node)


    def checkApplyIssue(self, node):
        """
        Check for apply issue in python 3(W9603).

        @param node: current node of checking
        """
        if not hasattr(node, "func"):
            return
        if not hasattr(node.func, "name"):
            return
        if (node.func.name != "apply" or
            type(node.func) != logilab.astng.node_classes.Name):
            return
        if not hasattr(node, "infered"):
            return
        inferedList = node.func.infered()
        if not inferedList:
            return
        inferedNode = inferedList[0]
        if not hasattr(inferedNode, "parent"):
            return
        if not hasattr(inferedNode.parent, "name"):
            return
        if inferedNode.parent.name == "__builtin__":
            self.add_message('W9603', node=node)


    def checkHasKeyIssue(self, node):
        """
        Check for has_key issue in python 3(W9602).

        @param node: current node of checking
        """
        issueFound = False
        # get the function
        func = node.func
        # get attribute name, if the node does not have 'attrname',
        # means that the node is a function call,
        # we should filter these usages and capture dict.has_key
        if not hasattr(func, "attrname"):
            return
        attrname = func.attrname
        # check whether this method is has_key
        if attrname != "has_key":
            return
        # now get the object which is called
        # it should be the first child of the method node
        objCalled = func.get_children().next()
        if isinstance(objCalled, logilab.astng.node_classes.Dict):
            # in this case, the statement should like
            # {}.has_key()
            issueFound = True
        else:
            # check for foo.has_key() and foo is defined as a dict
            # elsewhere
            # if an error is generated here, it means ast failed to
            # find the definition
            nodeArgument = node.func.last_child()
            if not nodeArgument:
                # no argument is used
                return
            try:
                objInferedList = nodeArgument.infered()
            except ASTNGError:
                # may be the name is unresolvable,
                # or definition is unreachable
                return
            if not objInferedList:
                # no infered node is found
                return
            objInfered = objInferedList[0]
            if isinstance(objInfered, logilab.astng.node_classes.Dict):
                issueFound = True

        if issueFound:
            self.add_message('W9602', node=node)
