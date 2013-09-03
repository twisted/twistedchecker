# -*- test-case-name: twistedchecker.test.test_docstring -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Classes and functions for checking docstrings for compliance with
the Twisted Coding Standard.
"""

import re

from logilab import astng
from logilab.astng import node_classes
from logilab.astng import scoped_nodes
from logilab.astng import nodes

from pylint.interfaces import IASTNGChecker
from pylint.checkers.base import DocStringChecker as PylintDocStringChecker
from pylint.checkers.base import NO_REQUIRED_DOC_RGX



def _closest(node, ancestorTypes):
    """
    Get the first element that is an instance of one of the
    C{ancestorTypes} by testing the C{node} itself and traversing up
    through its ancestors.

    @param node: The node on which to start the search
    @type node: L{logilab.astng.nodes}

    @param ancestorTypes: A tuple of node types to search for.
    @type ancestorTypes: L{tuple} of L{type}

    @return: the nearest matching node or L{None} if no matches.
    @rtype: L{logilab.astng.nodes} or L{None}
    """
    while node:
        if isinstance(node, ancestorTypes):
            return node
        node = getattr(node, 'parent', None)



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
    _closest = staticmethod(_closest)


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
        Check for missing, empty, or incorrectly formatted docstrings.

        @param node_type: type of node
        @param node: current node of pylint
        """
        if node.doc is None:
            # Missing docstring
            if type(node.parent) is scoped_nodes.Function:
                # Allow missing docstrings on nested functions
                return

            if self._docstringInherited(node):
                # Allow missing docstrings if there is an interface which has a
                # docstring for that function.
                return

            self.add_message('W9208', node=node)
            return

        if not node.doc.strip():
            # Empty docstring.
            self.add_message('W9209', node=node)
            return

        # Get line number of docstring.
        linenoDocstring = self._getDocstringLineno(node_type, node)
        self._checkDocstringFormat(node_type, node, linenoDocstring)
        self._checkEpytext(node_type, node, linenoDocstring)
        self._checkBlankLineBeforeEpytext(node_type, node, linenoDocstring)


    def _docstringInherited(self, node):
        """
        Check whether a node is part of a documented interface
        implementation.

        @param node: The node to inspect
        @type node: L{logilab.astng.scoped_nodes.Function}

        @return: L{True} if there is an interface function with the
            method name else L{False}.
        @rtype: L{bool}
        """
        if not isinstance(node, nodes.Function):
            # Only look for inherited docstrings in function nodes.
            return False

        if not node.is_method():
            # Only look for inherited docstrings if the node is a
            # method.
            return False

        parentClassNode = self._closest(node, nodes.Class)
        decorators = getattr(parentClassNode, 'decorators', None)
        if decorators:
            # Check for 'implementer' class decorators
            for decoratorNode in decorators.nodes:
                # Ignore simple non-parameterised decorators
                if not isinstance(decoratorNode, nodes.CallFunc):
                    continue
                # XXX: This is fragile, the zope.interface.implementer
                # decorator could have been imported with a different
                # name. Or there could be a non-zope decorators called
                # implementer.
                if decoratorNode.func.name == 'implementer':
                    for interfaceNode in decoratorNode.args:
                        interface = self._getInterface(
                            node, interfaceNode.as_string())
                        if interface is not None and node.name in interface:
                            return True

        return False


    def _getInterface(self, node, interfaceName):
        """
        Load an C{astng} representation of the given interface class.

        @param node: The method node which implement interface and
            whose root module contains or imports the interface.
        @type node: L{logilab.astng.nodes.Function}

        @param interfaceName: The qualified name of the
            interface class passed to the @implementer
            decorator.
        @type interfaceName: C{str}

        @return: The C{astng} node representing the named interface.
        @rtype: L{logilab.astng.nodes.Class}
        """
        interfaceNameSegments = interfaceName.split('.')
        interfaceClassName = interfaceNameSegments[-1]
        # Raises KeyError if interface name not found.
        matchingLocalNodes = node.root().locals[interfaceNameSegments[0]]
        # XXX: Safe to assume there's only one node with that name?
        interfaceImportNode = matchingLocalNodes[0]

        # Handle imported interfaces
        if isinstance(interfaceImportNode,
                      (astng.nodes.From, astng.nodes.Import)):
            # Now build the full path as a list. Handled differently
            # depending on whether the interface was imported using an
            # import or a from .. import statement.
            if isinstance(interfaceImportNode, astng.nodes.Import):
                interfaceNameSegmentsAbs = interfaceNameSegments

            elif isinstance(interfaceImportNode, astng.nodes.From):
                interfaceNameSegmentsAbs = (
                    interfaceImportNode.modname.split('.')
                    + interfaceNameSegments)

            # Load the module as astng (everything but the last part)
            moduleNode = node.root().import_module(
                '.'.join(interfaceNameSegmentsAbs[:-1]))

            try:
                interface = moduleNode[interfaceClassName]
            except KeyError:
                raise AssertionError(
                    'Interface not found. '
                    'name: %r, module: %r' % (interfaceClassName, moduleNode))

        # Handle locally defined interfaces.
        elif isinstance(interfaceImportNode, astng.nodes.Class):
            interface = interfaceImportNode
        else:
            raise AssertionError(
                'Unexpected interfaceNode type. '
                'Got: %r.' % (interfaceImportNode,)
            )

        assert isinstance(interface, nodes.Class), (
            'Unexpected interface type. '
            'interfaceName: %r, '
            'interface: %r.' % (interfaceName, interface))

        return  interface


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
        for argname in argnames:
            if not re.search(r"@param\s+%s\s*:" % argname, node.doc):
                self.add_message('W9202', line=linenoDocstring,
                                 node=node, args=argname)
            if not re.search(r"@type\s+%s\s*:" % argname, node.doc):
                self.add_message('W9203', line=linenoDocstring,
                                 node=node, args=argname)
        # Check for return value.
        if self._hasReturnValue(node):
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
        patternEpytext = (r"\n *@(param|type|return|returns|rtype)"
                          r"\s*[a-zA-Z0-9_]*\s*\:")
        matchedEpytext = re.search(patternEpytext, node.doc)
        if matchedEpytext:
            # This docstring have epytext markups,
            # then check the blank line before them.
            posEpytext = matchedEpytext.start() + 1
            if not re.search(r"\n\s*\n\s*$", node.doc[:posEpytext]):
                self.add_message('W9207', line=linenoDocstring, node=node)
