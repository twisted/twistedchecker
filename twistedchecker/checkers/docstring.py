import sys
import re

from logilab import astng
from logilab.common.ureports import Table
from logilab.astng import are_exclusive
from logilab.astng import node_classes

from pylint.interfaces import IASTNGChecker
from pylint.reporters import diff_string
from pylint.checkers.base import DocStringChecker as PylintDocStringChecker
from pylint.checkers.base import NO_REQUIRED_DOC_RGX


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
            # module starts from line 0
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
        if not docstring:
            # the node do not have a docstring
            return
        # get line number of docstring
        linenoDocstring = self._getDocstringLineno(node_type, node)
        self._checkDocstringFormat(node_type, node, linenoDocstring)
        self._checkEpytext(node_type, node, linenoDocstring)
        self._checkBlankLineBeforeEpytext(node_type, node, linenoDocstring)


    def _checkDocstringFormat(self, node_type, node, linenoDocstring):
        """
        Check opening/closing of docstring.

        @param node_type: type of node
        @param node: current node of pylint
        @param linenoDocstring: linenumber of docstring
        """
        # check the opening/closing of docstring
        docstringStripedSpaces = node.doc.strip(" ")
        if (not docstringStripedSpaces.startswith("\n")
            or not docstringStripedSpaces.endswith("\n")):
            self.add_message('W9201', line=linenoDocstring, node=node)
        else:
            # check indentation
            indentDocstring = node.col_offset and node.col_offset or 0
            indentDocstring += len(re.findall(r'\n( *)"""',
                                              node.as_string())[0])
            linesDocstring = node.doc.lstrip("\n").split("\n")
            for nline, lineDocstring in enumerate(linesDocstring):
                if (nline < len(linesDocstring) - 1
                    and not lineDocstring.strip()):
                    # its a blank line
                    continue
                if indentDocstring != self._getLineIndent(lineDocstring):
                    if node_type == "module":
                        lineno = linenoDocstring
                    else:
                        lineno = linenoDocstring + nline + 1
                    self.add_message('W9206', line=lineno, node=node)


    def _checkEpytext(self, node_type, node, linenoDocstring):
        """
        Check epytext of docstring.

        @param node_type: type of node
        @param node: current node of pylint
        @param linenoDocstring: linenumber of docstring
        """
        # check epytext markups
        if node_type in ["function", "method"]:
            # check for arguments
            for argname in node.argnames():
                if argname == 'self':
                    # argument self should not have a epytext markup
                    continue
                if not re.search(r"@param\s+%s\s*:" % argname, node.doc):
                    self.add_message('W9202', line=linenoDocstring, node=node)
                if not re.search(r"@type\s+%s\s*:" % argname, node.doc):
                    self.add_message('W9203', line=linenoDocstring, node=node)
            # check for return value
            returnFound = False
            for subnode in node.body:
                if type(subnode) == node_classes.Return:
                    returnFound = True
                    break
            if returnFound:
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
        # check whether there is a blank line before epytext markups
        patternEpytext = (r"\n *@(param|type|return|returns|rtype)"
                          r"\s*[a-zA-Z0-9_]*\s*\:")
        matchedEpytext = re.search(patternEpytext, node.doc)
        if matchedEpytext:
            # this docstring have epytext markups
            # then check the blank line
            posEpytext = matchedEpytext.start() + 1
            if not re.search(r"\n\s*\n\s*$", node.doc[:posEpytext]):
                self.add_message('W9207', line=linenoDocstring, node=node)
