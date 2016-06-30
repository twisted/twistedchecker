# -*- test-case-name: twistedchecker.test.test_functionaltests -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Checks for docstrings.
"""

import re

from logilab.astng import node_classes, scoped_nodes, YES
from logilab.astng.exceptions import InferenceError

from pylint.interfaces import IASTNGChecker
from pylint.checkers.base import DocStringChecker as PylintDocStringChecker
from pylint.checkers.base import NO_REQUIRED_DOC_RGX


def _isInner(node):
    """
    Determine whether the given node is, at any point in its syntactic
    parentage, defined within a function.

    @param node: The node to inspect.
    @type node: L{logilab.astng.bases.NodeNG}

    @return: a boolean indicating if the given node is defined as an inner
        class or inner function.
    """
    while node:
        node = node.parent
        if isinstance(node, scoped_nodes.Function):
            return True
    return False



def _getDecoratorsName(node):
    """
    Return a list with names of decorators attached to this node.

    @param node: current node of pylint
    """
    try:
        names = node.decoratornames()
    except InferenceError:
        # Sometimes astng fails by raising this kind of error.
        pass
    else:
        # Whereas sometimes it fails by returning this magic token.
        if YES not in names:
            return names
    # If pylint's attempt to discover the decorator's names has failed, fall
    # back to our own logic.
    decorators = []
    for decorator in node.decorators.nodes:
        decorators.append(decorator.as_string())
    return decorators


def _isSetter(node_type, node):
    """
    Determine whether the given node is a setter property.

    @param node_type: The type of the node to inspect.
    @param node: The L{logilab.astng.bases.NodeNG} to inspect.

    @return: a boolean indicating if the given node is a setter.
    """
    if node_type not in ['function', 'method']:
        return False

    for name in _getDecoratorsName(node):
        if '.setter' in name:
            return True
    return False


class DocstringChecker(PylintDocStringChecker):
    """
    A checker for checking docstrings.
    """
    msgs = {
     'W9201': ('The opening/closing of docstring should be on a line '
               'by themselves',
               'Check the opening/closing of a docstring.'),
     'W9202': ('Missing epytext markup @param for argument "%s"',
               'Check the epytext markup @param.'),
     'W9203': ('Missing epytext markup @type for argument "%s"',
               'Check the epytext markup @type.'),
     'W9204': ('Missing epytext markup @return for return value',
               'Check the epytext markup @return.'),
     'W9205': ('Missing epytext markup @rtype for return value',
               'Check the epytext markup @rtype.'),
     'W9206': ('Docstring should have consistent indentations',
               'Check indentations of docstring.'),
     'W9207': ('Missing a blank line before epytext markups',
               'Check the blank line before epytext markups.'),
     'W9208': ('Missing docstring',
               'Used when a module, function, class or method '
               'has no docstring.'),
     'W9209': ('Empty docstring',
               'Used when a module, function, class or method '
               'has an empty docstring.'),
    }
    __implements__ = IASTNGChecker
    name = 'docstring'
    options = ()


    def open(self):
        """
        Set a value to stats and config.
        """
        self.stats = None
        self.config.no_docstring_rgx = NO_REQUIRED_DOC_RGX


    def _getLineIndent(self, line):
        """
        Get indentation of a line.

        @param line: a line of code
        @return: number of spaces
        """
        return len(line) - len(line.lstrip(" "))


    def _getDocstringLineno(self, node_type, node):
        """
        Get line number of the docstring.

        @param node_type: type of node_type
        @param node: node of currently checking
        @return: line number
        """
        docstringStriped = node.as_string().strip()
        linenoDocstring = (node.lineno + docstringStriped
                           .count("\n", 0, docstringStriped.index('"""')))
        if node_type == "module":
            # Module starts from line 0.
            linenoDocstring += 1
        return linenoDocstring


    def _check_docstring(self, node_type, node):
        """
        Check whether the opening and the closing of docstring
        on a line by themselves.
        Then check for epytext markups for function or method.

        @param node_type: type of node
        @param node: current node of pylint
        """
        docstring = node.doc
        if docstring is None:
            # The node does not have a docstring.
            if _isInner(node):
                # Do not check things inside a function or method.
                return

            if _isSetter(node_type, node):
                # Setters don't need a docstring as they are documented in
                # the getter.
                return

            self.add_message('W9208', node=node)
            return
        elif not docstring.strip():
            # Empty docstring.
            self.add_message('W9209', node=node)
            return
        # Get line number of docstring.
        linenoDocstring = self._getDocstringLineno(node_type, node)
        self._checkDocstringFormat(node_type, node, linenoDocstring)
        self._checkEpytext(node_type, node, linenoDocstring)
        self._checkBlankLineBeforeEpytext(node_type, node, linenoDocstring)


    def _checkIndentationIssue(self, node, node_type, linenoDocstring):
        """
        Check whether a docstring have consistent indentations.

        @param node: the node currently checks by pylint
        @param node_type: type of given node
        @param linenoDocstring: line number the docstring begins
        """
        indentDocstring = node.col_offset and node.col_offset or 0
        indentDocstring += len(re.findall(r'\n( *)"""',
                                          node.as_string())[0])
        linesDocstring = node.doc.lstrip("\n").split("\n")
        for nline, lineDocstring in enumerate(linesDocstring):
            if (nline < len(linesDocstring) - 1
                and not lineDocstring.strip()):
                # It's a blank line.
                continue
            if indentDocstring != self._getLineIndent(lineDocstring):
                if node_type == "module":
                    lineno = linenoDocstring
                else:
                    lineno = linenoDocstring + nline + 1
                self.add_message('W9206', line=lineno, node=node)


    def _checkDocstringFormat(self, node_type, node, linenoDocstring):
        """
        Check opening/closing of docstring.

        @param node_type: type of node
        @param node: current node of pylint
        @param linenoDocstring: linenumber of docstring
        """
        # Check the opening/closing of docstring.
        docstringStrippedSpaces = node.doc.strip(" ")
        if (not docstringStrippedSpaces.startswith("\n")
            or not docstringStrippedSpaces.endswith("\n")):
            # If the docstring is in one line, then do not check indentations.
            self.add_message('W9201', line=linenoDocstring, node=node)
        else:
            # If the docstring's opening and closing quotes are on separate
            # lines, then we check its indentation.
            # Generating warnings about indentation when the quotes aren't
            # done right only clutters the output.
            self._checkIndentationIssue(node, node_type, linenoDocstring)


    def _hasReturnValue(self, node):
        """
        Determine whether the given method or function has a return statement.

        @param node: the node currently checks
        """
        returnFound = False
        for subnode in node.body:
            if type(subnode) == node_classes.Return and subnode.value:
                returnFound = True
                break
        return returnFound


    def _checkEpytext(self, node_type, node, linenoDocstring):
        """
        Check epytext of docstring.

        @param node_type: type of node
        @param node: current node of pylint
        @param linenoDocstring: linenumber of docstring
        """
        if node_type not in ['function', 'method']:
            return
        # Check for arguments.
        # If current node is method,
        # then first argument could not have a epytext markup.
        # The first argument usually named 'self'.
        argnames = (node.argnames()[1:] if node_type == 'method'
                    else node.argnames())

        if _isSetter(node_type, node):
           # For setter methods we remove the `value` argument as it
            # does not need to be documented.
            try:
                argnames.remove('value')
            except ValueError:
                # No `value` in arguments.
                pass

        for argname in argnames:
            if not re.search(r"@param\s+%s\s*:" % argname, node.doc):
                self.add_message('W9202', line=linenoDocstring,
                                 node=node, args=argname)
            if not re.search(r"@type\s+%s\s*:" % argname, node.doc):
                self.add_message('W9203', line=linenoDocstring,
                                 node=node, args=argname)

        self._checkReturnValueEpytext(node, linenoDocstring)


    def _checkReturnValueEpytext(self, node, linenoDocstring):
        """
        Check if return value is documented.

        @param node: current node of pylint
        @param linenoDocstring: linenumber of docstring
        """
        # Getter properties don't need to document their return value,
        # but then need to have a return value.
        if '__builtin__.property' in _getDecoratorsName(node):
            if self._hasReturnValue(node):
                # Getter properties don't need a docstring.
                return

        # Check for return value.
        if self._hasReturnValue(node):
            if node.name.startswith('test_'):
                # Ignore return documentation for test methods.
                return
            if not re.search(r"@return[s]{0,1}\s*:", node.doc):
                self.add_message('W9204', line=linenoDocstring, node=node)
            if not re.search(r"@rtype\s*:", node.doc):
                self.add_message('W9205', line=linenoDocstring, node=node)


    def _checkBlankLineBeforeEpytext(self, node_type, node, linenoDocstring):
        """
        Check whether there is a blank line before epytext.

        @param node_type: type of node
        @param node: current node of pylint
        @param linenoDocstring: linenumber of docstring
        """
        # Check whether there is a blank line before epytext markups.
        patternEpytext = (r"\n *@(param|type|return|returns|rtype|ivar|cvar"
                          r"|raises|raise)"
                          r"\s*[a-zA-Z0-9_]*\s*\:")
        matchedEpytext = re.search(patternEpytext, node.doc)
        if matchedEpytext:
            # This docstring have epytext markups,
            # then check the blank line before them.
            posEpytext = matchedEpytext.start() + 1
            if not re.search(r"\n\s*\n\s*$", node.doc[:posEpytext]):
                self.add_message('W9207', line=linenoDocstring, node=node)
