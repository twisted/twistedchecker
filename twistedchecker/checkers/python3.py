"""
Checker for python3 compatibility issues.
"""
import sys
import os
import re
from logilab import astng

import logilab.astng.node_classes
from logilab.astng.exceptions import ASTNGError

from pylint.interfaces import IASTNGChecker
from pylint.checkers import BaseChecker
from pylint.checkers import utils


class Python3Checker(BaseChecker):
    """
    Checker for python3 compatibility issues.
    """

    __implements__ = (IASTNGChecker,)
    name = 'python3'
    msgs = {
     'W9601': ('Use print() instead of print statement in Python 3',
               'Checking print statement for python 3.'),
     'W9602': ('dict.has_key() has been removed in python 3, '
               'use the in operator instead',
               'Checking has_key issue for python 3.'),
    }
    options = ()
    linesOfCurrentModule = None

    def visit_module(self, node):
        """
        Save lines of the module currently checking.

        @parm node: current node of checking
        """
        self.linesOfCurrentModule = node.file_stream.readlines()


    def visit_print(self, node):
        """
        Be invoked when visiting a print statement.

        @parm node: current node of checking
        """
        self.checkPrintStatement(node)


    def visit_callfunc(self, node):
        """
        Be invoked when visiting a function node.

        @parm node: current node of checking
        """
        self.checkHasKeyIssue(node)


    def checkHasKeyIssue(self, node):
        """
        Check for has_key issue in python 3(W9602).

        @parm node: current node of checking
        """
        issueFound = False
        # get the function
        func = node.func
        # get attribute name, if the node does not have 'attrname',
        # means that the node is a function call,
        # we should filter these usages and capture dict.has_key
        if not hasattr(func,"attrname"):
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


    def checkPrintStatement(self, node):
        """
        Check for print statement in python 3(W9601).

        @parm node: current node of checking
        """
        linenoBegin = node.fromlineno - 1
        linenoEnd = node.tolineno - 1
        if (not self.linesOfCurrentModule or
            linenoEnd >= len(self.linesOfCurrentModule)):
            # in the case, the code is not from a module exists
            return
        codeStatement = " ".join(
                [line.strip()
                 for line in \
                 self.linesOfCurrentModule[linenoBegin: linenoEnd + 1]])
        # check for parens
        # replace all child nodes(especially tuples) with X
        codeStatement = codeStatement.replace(" ", "")
        for childNode in node.get_children():
            # do not replace for empty tuple
            if childNode.as_string() == "()":
                continue
            codeChildNode = childNode.as_string().replace(" ", "")
            codeStatement = codeStatement.replace(codeChildNode, "X")
        if not re.search("print\(.*?\)", codeStatement):
            self.add_message('W9601', node=node)
