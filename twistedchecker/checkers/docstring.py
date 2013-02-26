import re

from logilab import astng
from logilab.astng import node_classes
from logilab.astng import scoped_nodes
from logilab.astng import nodes

from pylint.interfaces import IASTNGChecker
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
#        import pdb;pdb.set_trace()
        if docstring is None:
            # The node does not have a docstring.
            # But that's ok if this is part of a documented interface.
            # or if this is a nested function or method.
            if (not self._docStringInherited(node)
                and type(node.parent) is not scoped_nodes.Function):
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


    def _docStringInherited(self, node):
        """
        Check whether a node is part of a documented interface implementation.

        @param node: The node to inspect
        @type node: L{logilab.astng.scoped_nodes.Function}
        """
#        import pdb;pdb.set_trace()
        if (isinstance(node, nodes.Function)
            and node.type == 'method'
            and node.parent.decorators):

            # check for 'implementer' class decorators
            for n in node.parent.decorators.nodes:
                # n.as_string()
                # 'implementer(interfaces.IResolver)'
                m = re.match('implementer\(([^\)]+)\)', n.as_string())
                if m:
                    # could be interfaces.IResolver or simply IResolver
                    interface_references = m.group(1).split(',')
                    for interface_reference in interface_references:
                        if node.name in self._getInterface(
                            node, interface_reference.strip()):
                            return True

        return False


    def _getInterface(self, node, interface_reference):
        # if it contains . then it must have been imported
        # and we need to get the first part of the
        # reference
        interface_reference_parts = interface_reference.split('.')
        interface_node = (
            node.root().locals[interface_reference_parts[0]][0])

        # Handle imported interfaces
        # In this case the target interface is imported
        if isinstance(interface_node,
                      (astng.nodes.From, astng.nodes.Import)):
            # now build the full path e.g.
            # [twisted, internet, interfaces, IResolver]
            if isinstance(interface_node, astng.nodes.Import):
                interface_reference_absolute = interface_reference_parts
            elif isinstance(interface_node, astng.nodes.From):
                interface_reference_absolute = (
                    interface_node.modname.split('.')
                    + interface_reference_parts)
            else:
                raise AssertionError(
                    'Unexpected interface_node class %r' % (interface_node,))
            # import the module bit (everything but the last part)
            try:
                interface = __import__('.'.join(
                        interface_reference_absolute[:-1]))
            except ImportError:
#                import pdb; pdb.set_trace()
                raise
            for p in interface_reference_absolute[1:]:
                interface = getattr(interface, p)

        # Handle locally defined interfaces In this case
        # the interface is an astng Class instance which happens
        # to be iterable, just like a zope.interface
        elif isinstance(interface_node, astng.nodes.Class):
            interface = interface_node
        else:
            raise AssertionError('Unexpected interface node class %r' % (interface_node,))
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
